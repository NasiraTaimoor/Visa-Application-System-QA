"""Wallet financial-lifecycle service: verify, reserve, release (T094).

Enforces BR-007 (pending/reserved funds are not available), BR-022
(reservation happens immediately before sub-agency submission and is tied to
the validated snapshot and fee version), BR-024 (24h reservation expiry),
and BR-025 (concurrent actions cannot double-reserve the same funds — via
the idempotency store's unique key plus the ledger event's own unique
idempotency_key column as a second guard).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.applications.idempotency.idempotency_store import DuplicateRequestReplay, claim_or_replay
from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.finance.fee_calculation_service import calculate_fees
from src.finance.models.wallet_ledger_event import WalletLedgerEvent
from src.integrations.wallet_adapter import available_balance

RESERVATION_EXPIRY_HOURS = 24


class ApplicationNotFoundError(ValueError):
    pass


class InvalidWalletStateError(ValueError):
    pass


@dataclass(frozen=True)
class WalletVerificationOutcome:
    sufficient: bool
    amount: int
    currency: str
    fee_version: str
    available_balance_result: str
    reservation_reference: str | None
    shortfall_amount: int | None = None


def verify_and_reserve(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> WalletVerificationOutcome:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="wallet:verify",
            owning_agency_id=application.owning_sub_agency_id,
        )
    )

    if application.current_status != "ready_for_sub_agency_review":
        raise InvalidWalletStateError(
            "wallet verification requires status 'ready_for_sub_agency_review', "
            f"case is '{application.current_status}'"
        )

    fee = calculate_fees(application.visa_type)
    agency_id = application.owning_sub_agency_id
    balance = available_balance(db, agency_id)

    idempotency_key = f"wallet_reserve:{application_id}"
    reservation_reference: str | None = None
    result = "sufficient" if balance >= fee.amount else "shortfall"

    if result == "shortfall":
        db.add(
            WalletLedgerEvent(
                agency_id=agency_id,
                application_id=application_id,
                event_type="balance_check",
                amount=fee.amount,
                currency=fee.currency,
                fee_version=fee.fee_version,
                available_balance_result="shortfall",
                status="recorded",
                idempotency_key=f"balance_check:{application_id}:{datetime.now(timezone.utc).isoformat()}",
            )
        )
        db.commit()

        from src.notifications.notification_rules_engine import trigger_notification

        trigger_notification(db, application_id, "wallet_shortfall", correlation_reference)
    else:
        import uuid

        try:
            claim_or_replay(
                db, idempotency_key, scope="wallet_reserve", result_reference=application_id
            )
        except DuplicateRequestReplay:
            existing = (
                db.query(WalletLedgerEvent)
                .filter_by(application_id=application_id, event_type="reservation", status="active")
                .one_or_none()
            )
            if existing is not None:
                return WalletVerificationOutcome(
                    sufficient=True,
                    amount=existing.amount,
                    currency=existing.currency,
                    fee_version=existing.fee_version,
                    available_balance_result="sufficient",
                    reservation_reference=existing.reservation_reference,
                )

        reservation_reference = f"wal-res-{uuid.uuid4()}"
        db.add(
            WalletLedgerEvent(
                agency_id=agency_id,
                application_id=application_id,
                event_type="reservation",
                amount=fee.amount,
                currency=fee.currency,
                fee_version=fee.fee_version,
                available_balance_result="sufficient",
                reservation_reference=reservation_reference,
                status="active",
                idempotency_key=idempotency_key,
            )
        )
        result_transition = transition(application.current_status, "wallet_verified")
        application.current_status = result_transition.new_status
        application.fee_version = fee.fee_version
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=result_transition.previous_status,
                new_status=result_transition.new_status,
                source="finance_api",
                actor_or_service_id=identity.user_id,
                responsible_party=identity.role,
                next_action="Submit to main agency",
                correlation_reference=correlation_reference,
            )
        )
        db.commit()
        db.refresh(application)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=agency_id,
                action="wallet.verify",
                affected_case_or_record=application_id,
                outcome=result,
                source="finance_api",
                correlation_reference=correlation_reference,
            ),
        )

    return WalletVerificationOutcome(
        sufficient=result == "sufficient",
        amount=fee.amount,
        currency=fee.currency,
        fee_version=fee.fee_version,
        available_balance_result=result,
        reservation_reference=reservation_reference,
        shortfall_amount=(fee.amount - balance) if result == "shortfall" else None,
    )


def release_reservation(db: Session, application_id: str, reason: str) -> None:
    """Releases an active reservation (E-014 expiry, or finance action)."""
    reservation = (
        db.query(WalletLedgerEvent)
        .filter_by(application_id=application_id, event_type="reservation", status="active")
        .one_or_none()
    )
    if reservation is None:
        return
    reservation.status = "released"
    db.add(
        WalletLedgerEvent(
            agency_id=reservation.agency_id,
            application_id=application_id,
            event_type="release",
            amount=reservation.amount,
            currency=reservation.currency,
            fee_version=reservation.fee_version,
            release_reference=f"release-{reservation.wallet_event_id}",
            status="recorded",
            reason=reason,
            idempotency_key=f"release:{reservation.wallet_event_id}",
        )
    )
    db.commit()


def is_reservation_expired(reservation: WalletLedgerEvent) -> bool:
    return datetime.now(timezone.utc) - reservation.created_at > timedelta(
        hours=RESERVATION_EXPIRY_HOURS
    )
