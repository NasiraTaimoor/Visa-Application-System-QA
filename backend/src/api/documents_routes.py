"""Document, OCR, and validation API routes (T075)."""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_correlation_reference, get_identity
from src.auth.identity_provider import Identity
from src.db.session import get_db
from src.documents.document_service import replace_document, upload_document
from src.ocr.ocr_review_service import ConfirmOcrValuesCommand, confirm_ocr_values, get_ocr_result
from src.validation.override_service import ApproveOverrideCommand, approve_override
from src.validation.validation_engine import validate_application

router = APIRouter(tags=["documents"])


class ConfirmOcrValuesRequest(BaseModel):
    reviewed_values: dict = {}
    correction_reason: str | None = None


class ApproveOverrideRequest(BaseModel):
    reason: str


def _document_out(document) -> dict:
    return {
        "document_id": document.document_id,
        "document_type": document.document_type,
        "version": document.version,
        "upload_status": document.upload_status,
        "screening_status": document.screening_status,
    }


@router.post("/applications/{application_id}/documents")
def upload_document_endpoint(
    application_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    content = file.file.read()
    result = upload_document(
        db,
        identity,
        application_id,
        document_type,
        file.filename or "document",
        content,
        correlation_reference,
    )
    return {**_document_out(result.document), "ocr_triggered": result.ocr_triggered}


@router.post("/applications/{application_id}/documents/{document_id}/replace")
def replace_document_endpoint(
    application_id: str,
    document_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    content = file.file.read()
    result = replace_document(
        db,
        identity,
        application_id,
        document_id,
        file.filename or "document",
        content,
        correlation_reference,
    )
    return {**_document_out(result.document), "ocr_triggered": result.ocr_triggered}


@router.get("/documents/{document_id}/ocr")
def get_ocr_result_endpoint(document_id: str, db: Session = Depends(get_db)):
    result = get_ocr_result(db, document_id)
    return {
        "ocr_result_id": result.ocr_result_id,
        "document_id": result.document_id,
        "extraction_status": result.extraction_status,
        "extracted_fields": result.extracted_fields,
        "confidence_by_field": result.confidence_by_field,
        "overall_confidence": result.overall_confidence,
        "warning_flags": result.warning_flags,
        "reviewed_values": result.reviewed_values,
        "reviewer_id": result.reviewer_id,
    }


@router.post("/applications/{application_id}/documents/{document_id}/ocr/confirm")
def confirm_ocr_values_endpoint(
    application_id: str,
    document_id: str,
    payload: ConfirmOcrValuesRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    from src.applications.models.visa_application import VisaApplication

    application = db.get(VisaApplication, application_id)
    owning_agency_id = application.owning_sub_agency_id if application else None

    result = confirm_ocr_values(
        db,
        identity,
        application_id,
        owning_agency_id,
        ConfirmOcrValuesCommand(
            document_id=document_id,
            reviewed_values=payload.reviewed_values,
            correction_reason=payload.correction_reason,
            correlation_reference=correlation_reference,
        ),
    )
    return {
        "document_id": document_id,
        "reviewed_values": result.reviewed_values,
        "reviewer_id": result.reviewer_id,
    }


@router.post("/applications/{application_id}/validate")
def validate_application_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    outcome = validate_application(db, identity, application_id, correlation_reference)
    return {
        "current_status": outcome.current_status,
        "is_ready": outcome.is_ready,
        "findings": [
            {
                "finding_id": f.finding_id,
                "rule_id": f.rule_id,
                "severity": f.severity,
                "affected_field_or_document": f.affected_field_or_document,
                "corrective_action": f.corrective_action,
                "override_status": f.override_status,
            }
            for f in outcome.findings
        ],
    }


@router.post("/validation/findings/{finding_id}/override")
def approve_override_endpoint(
    finding_id: str,
    payload: ApproveOverrideRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    from src.applications.models.visa_application import VisaApplication
    from src.validation.models.validation_finding import ValidationFinding

    finding = db.get(ValidationFinding, finding_id)
    application = db.get(VisaApplication, finding.application_id) if finding else None
    owning_agency_id = application.owning_sub_agency_id if application else None

    result = approve_override(
        db,
        identity,
        owning_agency_id,
        ApproveOverrideCommand(
            finding_id=finding_id,
            reason=payload.reason,
            correlation_reference=correlation_reference,
        ),
    )
    return {"finding_id": result.finding_id, "override_status": result.override_status}
