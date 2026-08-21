"""Audit, search, export, and recovery API routes (T167)."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_correlation_reference, get_identity
from src.audit.audit_search_service import search_audit_events
from src.audit.store.base import get_audit_db
from src.audit.support_access_service import access_case_with_reason
from src.auth.identity_provider import Identity
from src.compliance.export_service import export_records
from src.db.session import get_db
from src.recovery.recovery_task_service import list_recovery_tasks, resolve_recovery_task

router = APIRouter(tags=["audit"])


class ExportRequest(BaseModel):
    application_id: str | None = None
    business_reason: str


class SupportAccessRequest(BaseModel):
    business_reason: str


class ResolveRecoveryTaskRequest(BaseModel):
    business_reason: str


@router.get("/audit/events")
def get_audit_history_endpoint(
    application_id: str | None = Query(default=None),
    audit_db: Session = Depends(get_audit_db),
    identity: Identity = Depends(get_identity),
):
    events = search_audit_events(audit_db, identity, application_id=application_id)
    return {"events": [e.__dict__ for e in events]}


@router.post("/audit/export")
def export_records_endpoint(
    payload: ExportRequest,
    audit_db: Session = Depends(get_audit_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    result = export_records(
        audit_db, identity, payload.application_id, payload.business_reason, correlation_reference
    )
    return {"export_reference": result.export_reference, "record_count": result.record_count}


@router.get("/recovery/tasks")
def get_recovery_tasks_endpoint(
    db: Session = Depends(get_db), identity: Identity = Depends(get_identity)
):
    tasks = list_recovery_tasks(db, identity)
    return {"tasks": [t.__dict__ for t in tasks]}


@router.post("/recovery/tasks/{task_id}/resolve")
def resolve_recovery_task_endpoint(
    task_id: str,
    payload: ResolveRecoveryTaskRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    task = resolve_recovery_task(
        db, identity, task_id, payload.business_reason, correlation_reference
    )
    return {"task_id": task.task_id, "status": task.status}


@router.post("/support/cases/{application_id}/access")
def support_access_endpoint(
    application_id: str,
    payload: SupportAccessRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    summary = access_case_with_reason(
        db, identity, application_id, payload.business_reason, correlation_reference
    )
    return {
        "application_id": summary.application_id,
        "case_reference": summary.case_reference,
        "current_status": summary.current_status,
        "applicant_legal_name_masked": summary.applicant_legal_name_masked,
    }
