"""OCR review/confirmation service applying confidence thresholds (T072).

BR-021: below 85% overall confidence requires manual confirmation; below 60%
requires manual entry or replacement document before submission. BR-003: OCR
output is advisory until reviewed and confirmed by an authorized user.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.config import get_policy_config
from src.ocr.models.ocr_result import OcrResult


class OcrResultNotFoundError(ValueError):
    pass


class ManualEntryRequiredError(ValueError):
    """Raised when confidence is below the blocking threshold and no
    reviewed values were supplied (E-018: OCR failure requires replacement
    or manual entry)."""


@dataclass(frozen=True)
class ConfirmOcrValuesCommand:
    document_id: str
    correlation_reference: str
    reviewed_values: dict = field(default_factory=dict)
    correction_reason: str | None = None


def get_ocr_result(db: Session, document_id: str) -> OcrResult:
    result = (
        db.query(OcrResult)
        .filter_by(document_id=document_id)
        .order_by(OcrResult.ocr_result_id.desc())
        .first()
    )
    if result is None:
        raise OcrResultNotFoundError(document_id)
    return result


def confirm_ocr_values(
    db: Session,
    identity: Identity,
    application_id: str,
    owning_agency_id: str,
    cmd: ConfirmOcrValuesCommand,
) -> OcrResult:
    authorize(
        AuthorizationContext(
            identity=identity,
            action="ocr:review_confirm",
            owning_agency_id=owning_agency_id if identity.role != "applicant" else None,
        )
    )

    result = get_ocr_result(db, cmd.document_id)
    policy = get_policy_config()

    below_blocking = (result.overall_confidence or 0) < policy.ocr_confidence_blocking_threshold
    if below_blocking and not cmd.reviewed_values:
        raise ManualEntryRequiredError(
            "confidence is below the blocking threshold; supply corrected values "
            "or replace the document"
        )

    result.reviewed_values = {**result.reviewed_values, **cmd.reviewed_values}
    result.reviewer_id = identity.user_id
    result.reviewed_at = datetime.now(timezone.utc)
    result.correction_reason = cmd.correction_reason
    db.commit()
    db.refresh(result)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=owning_agency_id,
                action="ocr.review_confirm",
                affected_case_or_record=application_id,
                outcome="success",
                source="documents_api",
                correlation_reference=cmd.correlation_reference,
                metadata_reference=cmd.document_id,
            ),
        )

    return result
