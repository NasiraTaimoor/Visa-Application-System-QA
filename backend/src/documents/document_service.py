"""Document upload/replace service with version history (T070).

Wires screening (T069), protected object storage (T012), and OCR
orchestration (T071, gated on passed screening) together, and advances the
case from `draft_created` to `documents_pending` on the first accepted
upload per the status transition matrix.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.documents.models.document import Document
from src.documents.screening_adapter import screen_document
from src.documents.storage.object_storage_adapter import get_object_storage_adapter
from src.ocr.ocr_orchestration_service import run_ocr

UPLOADABLE_STATUSES = frozenset(
    {"draft_created", "documents_pending", "ocr_and_validation", "correction_requested"}
)


class ApplicationNotFoundError(ValueError):
    pass


class InvalidUploadStateError(ValueError):
    pass


class DocumentNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class UploadDocumentResult:
    document: Document
    ocr_triggered: bool


def _authorize_write(
    identity: Identity, application: VisaApplication, action_owner: str, action_agency: str
) -> None:
    authorize(
        AuthorizationContext(
            identity=identity,
            action=action_owner if identity.role == "applicant" else action_agency,
            owning_agency_id=(
                application.owning_sub_agency_id if identity.role != "applicant" else None
            ),
        )
    )


def _advance_to_documents_pending(
    db: Session, identity: Identity, application: VisaApplication, correlation_reference: str
) -> None:
    if application.current_status != "draft_created":
        return
    result = transition(application.current_status, "documents_pending")
    application.current_status = result.new_status
    db.add(
        StatusEvent(
            application_id=application.application_id,
            previous_status=result.previous_status,
            new_status=result.new_status,
            source="documents_api",
            actor_or_service_id=identity.user_id,
            responsible_party=identity.role,
            next_action="Upload remaining required documents",
            correlation_reference=correlation_reference,
        )
    )


def upload_document(
    db: Session,
    identity: Identity,
    application_id: str,
    document_type: str,
    filename: str,
    content: bytes,
    correlation_reference: str,
) -> UploadDocumentResult:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    _authorize_write(identity, application, "document:upload_own", "document:upload_own_agency")

    if application.current_status not in UPLOADABLE_STATUSES:
        raise InvalidUploadStateError(
            f"documents cannot be uploaded while the case is '{application.current_status}'"
        )

    screening = screen_document(document_type, filename, content)
    storage = get_object_storage_adapter()
    file_reference = storage.store(application_id, filename, content)

    document = Document(
        application_id=application_id,
        document_type=document_type,
        file_reference=file_reference,
        file_metadata={"filename": filename, "size_bytes": len(content)},
        upload_actor_id=identity.user_id,
        upload_status="uploaded" if screening.accepted else "rejected",
        screening_status=screening.screening_status,
        verification_status="verified" if screening.accepted else "unverified",
    )
    db.add(document)
    db.flush()

    ocr_triggered = False
    from src.config import get_policy_config

    if screening.accepted:
        _advance_to_documents_pending(db, identity, application, correlation_reference)
        if document_type in get_policy_config().ocr_eligible_document_types:
            run_ocr(db, document, content)
            ocr_triggered = True

    db.commit()
    db.refresh(document)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.owning_sub_agency_id,
                action="document.upload",
                affected_case_or_record=application_id,
                outcome="success" if screening.accepted else "rejected",
                reason=screening.reject_reason_category,
                source="documents_api",
                correlation_reference=correlation_reference,
                metadata_reference=document.document_id,
            ),
        )

    return UploadDocumentResult(document=document, ocr_triggered=ocr_triggered)


def replace_document(
    db: Session,
    identity: Identity,
    application_id: str,
    document_id: str,
    filename: str,
    content: bytes,
    correlation_reference: str,
) -> UploadDocumentResult:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    _authorize_write(identity, application, "document:replace_own", "document:replace_own_agency")

    previous = db.get(Document, document_id)
    if previous is None or previous.application_id != application_id:
        raise DocumentNotFoundError(document_id)

    if application.current_status not in UPLOADABLE_STATUSES:
        raise InvalidUploadStateError(
            f"documents cannot be replaced while the case is '{application.current_status}'"
        )

    screening = screen_document(previous.document_type, filename, content)
    storage = get_object_storage_adapter()
    file_reference = storage.store(application_id, filename, content)

    new_document = Document(
        application_id=application_id,
        document_type=previous.document_type,
        file_reference=file_reference,
        file_metadata={"filename": filename, "size_bytes": len(content)},
        upload_actor_id=identity.user_id,
        upload_status="uploaded" if screening.accepted else "rejected",
        screening_status=screening.screening_status,
        verification_status="verified" if screening.accepted else "unverified",
        version=previous.version + 1,
        replaced_document_id=previous.document_id,
    )
    db.add(new_document)
    db.flush()

    # Replacement invalidates any stale OCR confirmation tied to the old document.
    ocr_triggered = False
    from src.config import get_policy_config

    if (
        screening.accepted
        and previous.document_type in get_policy_config().ocr_eligible_document_types
    ):
        run_ocr(db, new_document, content)
        ocr_triggered = True

    db.commit()
    db.refresh(new_document)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.owning_sub_agency_id,
                action="document.replace",
                affected_case_or_record=application_id,
                outcome="success" if screening.accepted else "rejected",
                reason=screening.reject_reason_category,
                source="documents_api",
                correlation_reference=correlation_reference,
                metadata_reference=new_document.document_id,
            ),
        )

    return UploadDocumentResult(document=new_document, ocr_triggered=ocr_triggered)
