"""Intake completeness/missing-item calculation service (T043)."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.applicant import Applicant
from src.applications.models.passport import Passport
from src.config import get_policy_config

REQUIRED_APPLICANT_FIELDS = ("legal_name", "date_of_birth", "nationality")
REQUIRED_PASSPORT_FIELDS = ("passport_number", "issuing_country", "issue_date", "expiry_date")


@dataclass(frozen=True)
class CompletenessResult:
    missing_items: tuple[str, ...]
    is_complete: bool


def calculate_missing_items(
    visa_type: str,
    applicant: Applicant,
    passport: Passport | None,
    accepted_document_types: frozenset[str] = frozenset(),
) -> CompletenessResult:
    policy = get_policy_config()
    missing: list[str] = []

    for field_name in REQUIRED_APPLICANT_FIELDS:
        if not getattr(applicant, field_name, None):
            missing.append(f"applicant.{field_name}")

    if passport is None:
        missing.extend(f"passport.{f}" for f in REQUIRED_PASSPORT_FIELDS)
    else:
        for field_name in REQUIRED_PASSPORT_FIELDS:
            if not getattr(passport, field_name, None):
                missing.append(f"passport.{field_name}")

    for document_type, applicable_visa_types in policy.document_requirements.items():
        if visa_type in applicable_visa_types and document_type not in accepted_document_types:
            missing.append(f"document.{document_type}")

    if not applicant.consent_records or "applicant_identity_data" not in applicant.consent_records:
        missing.append("consent.applicant_identity_data")

    return CompletenessResult(missing_items=tuple(missing), is_complete=len(missing) == 0)


def get_accepted_document_types(db: Session, application_id: str) -> frozenset[str]:
    from src.documents.models.document import Document

    rows = (
        db.query(Document.document_type)
        .filter_by(application_id=application_id, screening_status="accepted")
        .distinct()
        .all()
    )
    return frozenset(row[0] for row in rows)
