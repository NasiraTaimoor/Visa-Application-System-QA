"""Payment state service: required/pending/paid/failed/cancelled/refunded/
disputed/reconciled, enforcing BR-023 (wallet debit on payable, release on
early rejection/withdrawal) (T131)."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.idempotency.idempotency_store import DuplicateRequestReplay, claim_or_replay
from src.applications.models.applicant import Applicant
from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.finance.models.payment import Payment
from src.finance.models.wallet_ledger_event import WalletLedgerEvent
from src.integrations.payment_adapter import confirm_payment


class ApplicationNotFoundError(ValueError):
    pass


class InvalidPaymentStateError(ValueError):
    pass


@dataclass(frozen=True)
class PaymentOutcome:
    payment_state: str
    current_status: str
    reason: str | None


def _debit_reservation(db: Session, application: VisaApplication) -> None:
    reservation = (
        db.query(WalletLedgerEvent)
        .filter_by(
            application_id=application.application_id, event_type="reservation", status="active"
        )
        .one_or_none()
    )
    if reservation is None:
        return
    reservation.status = "settled"
    db.add(
        WalletLedgerEvent(
            agency_id=reservation.agency_id,
            application_id=application.application_id,
            event_type="debit",
            amount=reservation.amount,
            currency=reservation.currency,
            fee_version=reservation.fee_version,
            debit_reference=f"debit-{reservation.wallet_event_id}",
            status="active",
            idempotency_key=f"debit:{reservation.wallet_event_id}",
        )
    )


def confirm_payment_event(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> PaymentOutcome:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(AuthorizationContext(identity=identity, action="payment:record"))

    idempotency_key = f"payment_confirm:{application_id}"
    try:
        claim_or_replay(
            db, idempotency_key, scope="payment_confirm", result_reference=application_id
        )
    except DuplicateRequestReplay:
        existing = db.query(Payment).filter_by(idempotency_key=idempotency_key).one_or_none()
        if existing is not None:
            return PaymentOutcome(
                payment_state=existing.payment_state,
                current_status=application.current_status,
                reason=existing.reason,
            )
        raise

    if application.current_status not in ("payment_pending", "payment_failed"):
        raise InvalidPaymentStateError(
            "payment confirmation requires status 'payment_pending', "
            f"case is '{application.current_status}'"
        )

    applicant = db.get(Applicant, application.applicant_id)
    result = confirm_payment(applicant.legal_name or "")

    payment = Payment(
        application_id=application_id,
        payment_state=result.state,
        amount=0,
        currency="AED",
        fee_version=application.fee_version or "unknown",
        provider_reference=result.provider_reference,
        receipt_reference=result.receipt_reference,
        confirmation_source=identity.role,
        dispute_status="open" if result.state == "disputed" else None,
        reason=result.reason,
        idempotency_key=idempotency_key,
    )
    db.add(payment)

    if result.state == "paid":
        _debit_reservation(db, application)
        if application.current_status == "payment_failed":
            # payment_failed has no direct "paid" transition in the matrix;
            # a successful retry passes back through payment_pending first.
            retry_step = transition(application.current_status, "payment_pending")
            application.current_status = retry_step.new_status
            db.add(
                StatusEvent(
                    application_id=application_id,
                    previous_status=retry_step.previous_status,
                    new_status=retry_step.new_status,
                    source="payment_service",
                    actor_or_service_id=identity.user_id,
                    responsible_party="finance_officer",
                    next_action="Payment confirmed on retry",
                    correlation_reference=correlation_reference,
                )
            )
        step = transition(application.current_status, "paid")
        application.current_status = step.new_status
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=step.previous_status,
                new_status=step.new_status,
                source="payment_service",
                actor_or_service_id=identity.user_id,
                responsible_party="gdrfa_immigration_liaison",
                external_reference=result.provider_reference,
                next_action="Await immigration processing handoff",
                correlation_reference=correlation_reference,
            )
        )
    elif result.state == "failed" and application.current_status == "payment_pending":
        step = transition(application.current_status, "payment_failed")
        application.current_status = step.new_status
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=step.previous_status,
                new_status=step.new_status,
                source="payment_service",
                actor_or_service_id=identity.user_id,
                responsible_party="finance_officer",
                reason=result.reason,
                next_action="Resolve payment issue and retry",
                correlation_reference=correlation_reference,
            )
        )
    # "disputed" keeps the case in its current payment status and routes to finance review (E-007).

    db.commit()
    db.refresh(application)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.owning_sub_agency_id,
                action="payment.confirm",
                affected_case_or_record=application_id,
                outcome=result.state,
                reason=result.reason,
                source="payment_service",
                correlation_reference=correlation_reference,
            ),
        )

    from src.notifications.notification_rules_engine import trigger_notification

    trigger_notification(db, application_id, "payment_outcome", correlation_reference)

    return PaymentOutcome(
        payment_state=result.state, current_status=application.current_status, reason=result.reason
    )
