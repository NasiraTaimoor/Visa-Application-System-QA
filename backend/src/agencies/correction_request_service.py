"""Correction request service: reason, responsible party, due date (T110)."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.agencies.models.processing_task import ProcessingTask
from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity


class ApplicationNotFoundError(ValueError):
    pass


class ReasonRequiredError(ValueError):
    pass


@dataclass(frozen=True)
class RequestCorrectionCommand:
    application_id: str
    reason: str
    responsible_party: str
    correlation_reference: str
    due_in_days: int = 7


def request_correction(
    db: Session, identity: Identity, cmd: RequestCorrectionCommand
) -> VisaApplication:
    if not cmd.reason:
        raise ReasonRequiredError("a correction reason is required")

    application = db.get(VisaApplication, cmd.application_id)
    if application is None:
        raise ApplicationNotFoundError(cmd.application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="case:correction_request",
            owning_agency_id=application.routed_main_agency_id,
            business_reason=cmd.reason,
            requires_reason=True,
        )
    )

    result = transition(application.current_status, "correction_requested")
    application.current_status = result.new_status
    db.add(
        StatusEvent(
            application_id=cmd.application_id,
            previous_status=result.previous_status,
            new_status=result.new_status,
            source="main_agency_api",
            actor_or_service_id=identity.user_id,
            responsible_party=cmd.responsible_party,
            reason=cmd.reason,
            next_action="Resolve the requested correction",
            correlation_reference=cmd.correlation_reference,
        )
    )
    db.add(
        ProcessingTask(
            application_id=cmd.application_id,
            task_type="correction",
            assigned_role=cmd.responsible_party,
            owning_agency_id=application.owning_sub_agency_id,
            status="open",
            due_at=datetime.now(timezone.utc) + timedelta(days=cmd.due_in_days),
            reason=cmd.reason,
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
                agency_scope=application.routed_main_agency_id,
                action="case.correction_request",
                affected_case_or_record=cmd.application_id,
                outcome="success",
                reason=cmd.reason,
                source="main_agency_api",
                correlation_reference=cmd.correlation_reference,
            ),
        )

    from src.notifications.notification_rules_engine import trigger_notification

    trigger_notification(db, cmd.application_id, "correction_requested", cmd.correlation_reference)

    return application


def resolve_correction(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> VisaApplication:
    """Responsible party marks the correction as addressed, returning the
    case to main agency processing for re-review."""
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action=(
                "intake:write_own" if identity.role == "applicant" else "intake:write_own_agency"
            ),
            owning_agency_id=(
                application.owning_sub_agency_id if identity.role != "applicant" else None
            ),
        )
    )

    result = transition(application.current_status, "main_agency_processing")
    application.current_status = result.new_status
    db.add(
        StatusEvent(
            application_id=application_id,
            previous_status=result.previous_status,
            new_status=result.new_status,
            source="main_agency_api",
            actor_or_service_id=identity.user_id,
            responsible_party=identity.role,
            next_action="Main agency re-review",
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
                agency_scope=application.owning_sub_agency_id,
                action="case.correction_resolved",
                affected_case_or_record=application_id,
                outcome="success",
                source="main_agency_api",
                correlation_reference=correlation_reference,
            ),
        )

    return application
