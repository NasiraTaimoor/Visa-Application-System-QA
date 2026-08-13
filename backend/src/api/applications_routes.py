"""Application intake API routes (T048)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_correlation_reference, get_idempotency_key, get_identity
from src.applications.intake.abandon_draft import AbandonDraftCommand, abandon_draft
from src.applications.intake.create_application import CreateApplicationCommand, create_application
from src.applications.intake.resume_draft import resume_draft
from src.applications.intake.update_intake import UpdateIntakeCommand, update_intake
from src.auth.identity_provider import Identity
from src.db.session import get_db

router = APIRouter(prefix="/applications", tags=["applications"])


class CreateApplicationRequest(BaseModel):
    visa_type: str
    owning_sub_agency_id: str
    consent_given: bool
    legal_name: str | None = None


class UpdateIntakeRequest(BaseModel):
    expected_version: int
    applicant_fields: dict = {}
    passport_fields: dict = {}


class AbandonDraftRequest(BaseModel):
    reason: str


@router.post("")
def create_application_endpoint(
    payload: CreateApplicationRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
    idempotency_key: str | None = Depends(get_idempotency_key),
):
    application = create_application(
        db,
        identity,
        CreateApplicationCommand(
            visa_type=payload.visa_type,
            owning_sub_agency_id=payload.owning_sub_agency_id,
            consent_given=payload.consent_given,
            legal_name=payload.legal_name,
            correlation_reference=correlation_reference,
            idempotency_key=idempotency_key,
        ),
    )
    return {
        "application_id": application.application_id,
        "case_reference": application.case_reference,
        "current_status": application.current_status,
        "current_version": application.current_version,
        "correlation_reference": correlation_reference,
    }


@router.patch("/{application_id}")
def update_intake_endpoint(
    application_id: str,
    payload: UpdateIntakeRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    application, completeness = update_intake(
        db,
        identity,
        UpdateIntakeCommand(
            application_id=application_id,
            expected_version=payload.expected_version,
            applicant_fields=payload.applicant_fields,
            passport_fields=payload.passport_fields,
            correlation_reference=correlation_reference,
        ),
    )
    return {
        "application_id": application.application_id,
        "current_version": application.current_version,
        "missing_items": list(completeness.missing_items),
    }


@router.get("/{application_id}/resume")
def resume_draft_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
):
    summary = resume_draft(db, identity, application_id)
    return {
        "application_id": summary.application.application_id,
        "case_reference": summary.application.case_reference,
        "current_status": summary.application.current_status,
        "current_version": summary.application.current_version,
        "visa_type": summary.application.visa_type,
        "applicant": summary.applicant_masked,
        "missing_items": list(summary.missing_items),
    }


@router.post("/{application_id}/abandon")
def abandon_draft_endpoint(
    application_id: str,
    payload: AbandonDraftRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    application = abandon_draft(
        db,
        identity,
        AbandonDraftCommand(
            application_id=application_id,
            reason=payload.reason,
            correlation_reference=correlation_reference,
        ),
    )
    return {
        "application_id": application.application_id,
        "current_status": application.current_status,
    }
