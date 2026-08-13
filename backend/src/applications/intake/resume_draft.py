"""Resume draft command with role-based data masking (T046)."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.intake.completeness_service import (
    calculate_missing_items,
    get_accepted_document_types,
)
from src.applications.models.applicant import Applicant
from src.applications.models.passport import Passport
from src.applications.models.visa_application import VisaApplication
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity

APPLICANT_MASKED_FIELDS = ("date_of_birth",)


class DraftNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class ResumeDraftSummary:
    application: VisaApplication
    applicant_masked: dict
    missing_items: tuple[str, ...]


def _mask(value: str | None) -> str | None:
    if not value:
        return value
    return f"***{value[-2:]}" if len(value) > 2 else "***"


def resume_draft(db: Session, identity: Identity, application_id: str) -> ResumeDraftSummary:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise DraftNotFoundError(application_id)

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

    applicant = db.get(Applicant, application.applicant_id)
    passport = db.query(Passport).filter_by(application_id=application.application_id).one_or_none()
    accepted_document_types = get_accepted_document_types(db, application.application_id)
    completeness = calculate_missing_items(
        application.visa_type, applicant, passport, accepted_document_types
    )

    masked = {
        "legal_name": applicant.legal_name,
        "nationality": applicant.nationality,
        "date_of_birth": (
            _mask(applicant.date_of_birth)
            if not identity.is_privileged
            else applicant.date_of_birth
        ),
    }

    return ResumeDraftSummary(
        application=application, applicant_masked=masked, missing_items=completeness.missing_items
    )
