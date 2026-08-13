"""Sub-agency submission service: snapshot lock, single reservation,
submission reference, idempotency key (T095)."""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.idempotency.idempotency_store import DuplicateRequestReplay, claim_or_replay
from src.applications.models.status_event import StatusEvent
from src.applications.models.submission import Submission
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.config import get_policy_config
from src.finance.models.wallet_ledger_event import WalletLedgerEvent


class ApplicationNotFoundError(ValueError):
    pass


class InvalidSubmissionStateError(ValueError):
    pass


class NoActiveReservationError(ValueError):
    pass


@dataclass(frozen=True)
class SubmissionResult:
    submission_reference: str
    snapshot_id: str
    current_status: str


def submit_to_main_agency(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> SubmissionResult:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="submission:submit_main_agency",
            owning_agency_id=application.owning_sub_agency_id,
        )
    )

    idempotency_key = f"submit_main_agency:{application_id}"
    try:
        claim_or_replay(
            db, idempotency_key, scope="submit_main_agency", result_reference=application_id
        )
    except DuplicateRequestReplay:
        existing = db.query(Submission).filter_by(idempotency_key=idempotency_key).one_or_none()
        if existing is not None:
            return SubmissionResult(
                submission_reference=existing.submission_reference,
                snapshot_id=existing.snapshot_id,
                current_status=application.current_status,
            )
        raise

    if application.current_status != "wallet_verified":
        raise InvalidSubmissionStateError(
            f"submission requires status 'wallet_verified', case is '{application.current_status}'"
        )

    reservation = (
        db.query(WalletLedgerEvent)
        .filter_by(application_id=application_id, event_type="reservation", status="active")
        .one_or_none()
    )
    if reservation is None:
        raise NoActiveReservationError("no active wallet reservation exists for this application")

    policy = get_policy_config()
    target_agency = (
        policy.agency_hierarchy.get(application.owning_sub_agency_id) or "main-agency-root"
    )
    snapshot_id = f"snapshot-{application_id}-v{application.current_version}"
    submission_reference = f"SUB-{uuid.uuid4().hex[:12].upper()}"

    submission = Submission(
        application_id=application_id,
        submission_type="sub_agency",
        source_agency_id=application.owning_sub_agency_id,
        target_agency_or_system=target_agency,
        snapshot_id=snapshot_id,
        submission_reference=submission_reference,
        status="submitted",
        idempotency_key=idempotency_key,
    )
    db.add(submission)

    application.validated_snapshot_id = snapshot_id
    application.routed_main_agency_id = target_agency
    result = transition(application.current_status, "submitted_to_main_agency")
    application.current_status = result.new_status
    db.add(
        StatusEvent(
            application_id=application_id,
            previous_status=result.previous_status,
            new_status=result.new_status,
            source="finance_api",
            actor_or_service_id=identity.user_id,
            responsible_party=identity.role,
            external_reference=submission_reference,
            next_action="Await main agency assignment",
            correlation_reference=correlation_reference,
        )
    )
    db.commit()
    db.refresh(submission)
    db.refresh(application)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.owning_sub_agency_id,
                action="submission.submit_main_agency",
                affected_case_or_record=application_id,
                outcome="success",
                source="finance_api",
                correlation_reference=correlation_reference,
                metadata_reference=submission_reference,
            ),
        )

    from src.notifications.notification_rules_engine import trigger_notification

    trigger_notification(db, application_id, "submission_created", correlation_reference)

    return SubmissionResult(
        submission_reference=submission_reference,
        snapshot_id=snapshot_id,
        current_status=application.current_status,
    )
