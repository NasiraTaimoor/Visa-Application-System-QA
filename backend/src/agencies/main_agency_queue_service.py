"""Main agency routing/queue/assignment service (T109)."""

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


class InvalidQueueStateError(ValueError):
    pass


def claim_for_processing(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> VisaApplication:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="case:process",
            owning_agency_id=application.routed_main_agency_id,
        )
    )

    if application.current_status != "submitted_to_main_agency":
        raise InvalidQueueStateError(
            f"case cannot be claimed while status is '{application.current_status}'"
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
            next_action="Review case and decide next action",
            correlation_reference=correlation_reference,
        )
    )
    db.add(
        ProcessingTask(
            application_id=application_id,
            task_type="main_agency_review",
            assigned_role=identity.role,
            assigned_user_id=identity.user_id,
            owning_agency_id=application.routed_main_agency_id or "main-agency-root",
            status="open",
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
                action="case.claim",
                affected_case_or_record=application_id,
                outcome="success",
                source="main_agency_api",
                correlation_reference=correlation_reference,
            ),
        )

    return application
