"""Immigration status service with source validation and quarantine of
contradictory/unmatched updates (T134)."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.agencies.models.processing_task import ProcessingTask
from src.applications.models.applicant import Applicant
from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.applications.workflow.terminal_lock_service import ensure_not_locked
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.integrations.immigration_adapter import get_immigration_update
from src.integrations.models.external_case_response import ExternalCaseResponse

DECISION_TO_STATUS = {"approved": "approved", "rejected": "rejected"}


class ApplicationNotFoundError(ValueError):
    pass


class InvalidImmigrationStateError(ValueError):
    pass


@dataclass(frozen=True)
class ImmigrationUpdateOutcome:
    response_type: str
    current_status: str
    quarantined: bool
    reason: str | None


def record_immigration_update(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> ImmigrationUpdateOutcome:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(AuthorizationContext(identity=identity, action="immigration:record_update"))
    ensure_not_locked(application)

    if application.current_status == "paid":
        # First handoff into immigration processing (external case reference
        # requirement is satisfied by the case itself once payment is complete).
        step = transition(application.current_status, "immigration_processing")
        application.current_status = step.new_status
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=step.previous_status,
                new_status=step.new_status,
                source="immigration_service",
                actor_or_service_id=identity.user_id,
                responsible_party="gdrfa_immigration_liaison",
                next_action="Awaiting immigration decision",
                correlation_reference=correlation_reference,
            )
        )

    if application.current_status != "immigration_processing":
        raise InvalidImmigrationStateError(
            "immigration updates require status 'immigration_processing', "
            f"case is '{application.current_status}'"
        )

    applicant = db.get(Applicant, application.applicant_id)
    result = get_immigration_update(applicant.legal_name or "")

    import uuid

    if result.response_type == "contradictory":
        db.add(
            ExternalCaseResponse(
                application_id=application_id,
                source_system="immigration",
                external_reference=result.external_reference or f"imm-quarantine-{uuid.uuid4()}",
                response_type=result.response_type,
                reason=result.reason,
                matched_status="unmatched",
                quarantine_reason=result.reason,
                idempotency_key=f"immigration_update:{application_id}:{uuid.uuid4()}",
            )
        )
        db.commit()
        with AuditSessionLocal() as audit_db:
            record_audit_event(
                audit_db,
                AuditEventInput(
                    actor_or_service_id=identity.user_id,
                    role=identity.role,
                    action="immigration.update_quarantined",
                    affected_case_or_record=application_id,
                    outcome="quarantined",
                    reason=result.reason,
                    source="immigration_service",
                    correlation_reference=correlation_reference,
                ),
            )
        return ImmigrationUpdateOutcome(
            response_type=result.response_type,
            current_status=application.current_status,
            quarantined=True,
            reason=result.reason,
        )

    db.add(
        ExternalCaseResponse(
            application_id=application_id,
            source_system="immigration",
            external_reference=result.external_reference or f"imm-{uuid.uuid4()}",
            response_type=result.response_type,
            status_value=result.decision,
            reason=result.reason,
            matched_status="matched",
            idempotency_key=f"immigration_update:{application_id}:{uuid.uuid4()}",
        )
    )

    if result.response_type == "action_required":
        db.add(
            ProcessingTask(
                application_id=application_id,
                task_type="immigration_action_required",
                assigned_role="gdrfa_immigration_liaison",
                owning_agency_id=application.routed_main_agency_id or "main-agency-root",
                status="open",
                reason=result.reason,
            )
        )
    elif result.response_type == "final_decision":
        target_status = DECISION_TO_STATUS.get(result.decision or "", "rejected")
        step = transition(application.current_status, target_status)
        application.current_status = step.new_status
        application.terminal_outcome = target_status
        from datetime import datetime, timezone

        application.terminal_locked_at = datetime.now(timezone.utc)
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=step.previous_status,
                new_status=step.new_status,
                source="immigration_service",
                actor_or_service_id=identity.user_id,
                responsible_party="gdrfa_immigration_liaison",
                reason=result.reason,
                external_reference=result.external_reference,
                next_action="Case closed to further ordinary changes",
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
                action="immigration.update",
                affected_case_or_record=application_id,
                outcome=result.response_type,
                reason=result.reason,
                source="immigration_service",
                correlation_reference=correlation_reference,
            ),
        )

    from src.notifications.notification_rules_engine import trigger_notification

    event_type = (
        "final_decision" if result.response_type == "final_decision" else "immigration_event"
    )
    trigger_notification(db, application_id, event_type, correlation_reference)

    return ImmigrationUpdateOutcome(
        response_type=result.response_type,
        current_status=application.current_status,
        quarantined=False,
        reason=result.reason,
    )
