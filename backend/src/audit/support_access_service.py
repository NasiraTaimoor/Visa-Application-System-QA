"""Support access reason capture and audit linkage (T166).

BR-035: support admins may perform controlled recovery actions only with a
business reason and may not approve eligibility, financial, or terminal
decision outcomes. This service provides masked, read-only case lookup.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.applicant import Applicant
from src.applications.models.visa_application import VisaApplication
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity


class ReasonRequiredError(ValueError):
    pass


class ApplicationNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class MaskedCaseSummary:
    application_id: str
    case_reference: str
    current_status: str
    applicant_legal_name_masked: str | None


def _mask_name(value: str | None) -> str | None:
    if not value:
        return value
    parts = value.split(" ")
    return (
        " ".join([parts[0]] + ["*" * len(p) for p in parts[1:]])
        if len(parts) > 1
        else f"{value[0]}***"
    )


def access_case_with_reason(
    db: Session,
    identity: Identity,
    application_id: str,
    business_reason: str,
    correlation_reference: str,
) -> MaskedCaseSummary:
    if not business_reason:
        raise ReasonRequiredError("a business reason is required for support access to case data")

    authorize(
        AuthorizationContext(
            identity=identity,
            action="case:search_masked",
            business_reason=business_reason,
            requires_reason=True,
        )
    )

    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)
    applicant = db.get(Applicant, application.applicant_id)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                action="support.access",
                affected_case_or_record=application_id,
                outcome="success",
                reason=business_reason,
                source="audit_api",
                correlation_reference=correlation_reference,
            ),
        )

    return MaskedCaseSummary(
        application_id=application.application_id,
        case_reference=application.case_reference,
        current_status=application.current_status,
        applicant_legal_name_masked=_mask_name(applicant.legal_name if applicant else None),
    )
