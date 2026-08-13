"""Consent capture linked to Consent and Retention Policy (T042)."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.applications.models.applicant import Applicant
from src.compliance.models.consent_retention_policy import enforce_policy_exists


class ConsentRequiredError(ValueError):
    pass


def capture_consent(
    db: Session,
    applicant: Applicant,
    consent_given: bool,
    policy_id: str = "applicant_identity_data",
) -> None:
    policy = enforce_policy_exists(db, policy_id)
    if policy.consent_required and not consent_given:
        raise ConsentRequiredError("consent is required before an application can be created")

    records = dict(applicant.consent_records or {})
    records[policy_id] = {
        "given": consent_given,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    applicant.consent_records = records
