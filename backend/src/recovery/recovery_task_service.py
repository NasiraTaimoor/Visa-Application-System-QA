"""Recovery task query and resolution service (T165)."""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.agencies.models.processing_task import ProcessingTask
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity


class ReasonRequiredError(ValueError):
    pass


class TaskNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class RecoveryTaskView:
    task_id: str
    application_id: str
    task_type: str
    assigned_role: str
    status: str
    reason: str | None


def list_recovery_tasks(db: Session, identity: Identity) -> list[RecoveryTaskView]:
    authorize(AuthorizationContext(identity=identity, action="recovery:read"))

    tasks = (
        db.query(ProcessingTask)
        .filter(ProcessingTask.status == "open")
        .order_by(ProcessingTask.created_at.asc())
        .all()
    )
    return [
        RecoveryTaskView(
            task_id=t.task_id,
            application_id=t.application_id,
            task_type=t.task_type,
            assigned_role=t.assigned_role,
            status=t.status,
            reason=t.reason,
        )
        for t in tasks
    ]


def resolve_recovery_task(
    db: Session, identity: Identity, task_id: str, business_reason: str, correlation_reference: str
) -> RecoveryTaskView:
    if not business_reason:
        raise ReasonRequiredError("a business reason is required to resolve a recovery task")

    authorize(
        AuthorizationContext(
            identity=identity,
            action="recovery:resolve",
            business_reason=business_reason,
            requires_reason=True,
        )
    )

    task = db.get(ProcessingTask, task_id)
    if task is None:
        raise TaskNotFoundError(task_id)

    task.status = "resolved"
    task.completed_at = datetime.now(timezone.utc)
    task.recovery_context = business_reason
    db.commit()
    db.refresh(task)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=task.owning_agency_id,
                action="recovery.resolve",
                affected_case_or_record=task.application_id,
                outcome="success",
                reason=business_reason,
                source="audit_api",
                correlation_reference=correlation_reference,
                metadata_reference=task.task_id,
            ),
        )

    return RecoveryTaskView(
        task_id=task.task_id,
        application_id=task.application_id,
        task_type=task.task_type,
        assigned_role=task.assigned_role,
        status=task.status,
        reason=task.reason,
    )
