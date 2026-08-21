"""Main agency processing and GDRFA API routes (T114)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.agencies.correction_request_service import (
    RequestCorrectionCommand,
    request_correction,
    resolve_correction,
)
from src.agencies.main_agency_queue_service import claim_for_processing
from src.agencies.readiness_approval_service import ApproveReadinessCommand, approve_readiness
from src.api.deps import get_correlation_reference, get_identity
from src.auth.identity_provider import Identity
from src.db.session import get_db
from src.integrations.gdrfa_response_service import submit_and_handle_response

router = APIRouter(tags=["main-agency"])


class RequestCorrectionRequest(BaseModel):
    reason: str
    responsible_party: str = "applicant"
    due_in_days: int = 7


class ApproveReadinessRequest(BaseModel):
    reason: str


def _application_out(application) -> dict:
    return {
        "application_id": application.application_id,
        "current_status": application.current_status,
    }


@router.post("/applications/{application_id}/claim")
def claim_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    application = claim_for_processing(db, identity, application_id, correlation_reference)
    return _application_out(application)


@router.post("/applications/{application_id}/correction-request")
def request_correction_endpoint(
    application_id: str,
    payload: RequestCorrectionRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    application = request_correction(
        db,
        identity,
        RequestCorrectionCommand(
            application_id=application_id,
            reason=payload.reason,
            responsible_party=payload.responsible_party,
            due_in_days=payload.due_in_days,
            correlation_reference=correlation_reference,
        ),
    )
    return _application_out(application)


@router.post("/applications/{application_id}/correction-resolve")
def resolve_correction_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    application = resolve_correction(db, identity, application_id, correlation_reference)
    return _application_out(application)


@router.post("/applications/{application_id}/readiness-approve")
def approve_readiness_endpoint(
    application_id: str,
    payload: ApproveReadinessRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    application = approve_readiness(
        db,
        identity,
        ApproveReadinessCommand(
            application_id=application_id,
            reason=payload.reason,
            correlation_reference=correlation_reference,
        ),
    )
    return _application_out(application)


@router.post("/applications/{application_id}/gdrfa/submit")
def submit_gdrfa_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    outcome = submit_and_handle_response(db, identity, application_id, correlation_reference)
    return {
        "submission_reference": outcome.submission_reference,
        "response_type": outcome.response_type,
        "current_status": outcome.current_status,
        "response_reason": outcome.response_reason,
    }
