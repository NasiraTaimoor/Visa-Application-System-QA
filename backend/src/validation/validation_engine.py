"""Validation rules engine: required fields, document presence, passport
rules, visa-type rules, duplicate risk, and agency rules, with severity
outcomes (T073). Also advances the case through `documents_pending` ->
`ocr_and_validation` -> `ready_for_sub_agency_review` per the status
transition matrix once its preconditions are met.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.applications.intake.completeness_service import calculate_missing_items
from src.applications.models.applicant import Applicant
from src.applications.models.passport import Passport
from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.config import get_policy_config
from src.documents.models.document import Document
from src.ocr.models.ocr_result import OcrResult
from src.validation.models.validation_finding import ValidationFinding

RULE_VERSION = "1"

OCR_FIELD_TO_APPLICANT = {"date_of_birth": "date_of_birth", "nationality": "nationality"}
OCR_FIELD_TO_PASSPORT = {"passport_number": "passport_number", "expiry_date": "expiry_date"}


class ApplicationNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class ValidationOutcome:
    findings: list[ValidationFinding]
    current_status: str
    is_ready: bool


def _unresolved_blocking(findings: list[ValidationFinding]) -> list[ValidationFinding]:
    unresolved = []
    for finding in findings:
        if finding.severity == "informational" or finding.result == "pass":
            continue
        if finding.severity == "warning":
            continue
        if finding.override_status == "approved":
            continue
        unresolved.append(finding)
    return unresolved


def _document_findings(db: Session, application: VisaApplication) -> list[ValidationFinding]:
    policy = get_policy_config()
    accepted_types = {
        d.document_type
        for d in db.query(Document)
        .filter_by(application_id=application.application_id, screening_status="accepted")
        .all()
    }
    findings = []
    for document_type, applicable_visa_types in policy.document_requirements.items():
        if application.visa_type not in applicable_visa_types:
            continue
        if document_type in accepted_types:
            continue
        severity = (
            "non_overrideable_blocking"
            if document_type == "passport_bio_page"
            else "overrideable_blocking"
        )
        findings.append(
            ValidationFinding(
                application_id=application.application_id,
                rule_id="document_presence",
                rule_version=RULE_VERSION,
                result="fail",
                severity=severity,
                affected_field_or_document=f"document.{document_type}",
                responsible_party="applicant",
                corrective_action=f"Upload an accepted {document_type.replace('_', ' ')}",
            )
        )
    return findings


def _passport_validity_findings(
    application: VisaApplication, passport: Passport | None
) -> list[ValidationFinding]:
    if passport is None or not passport.expiry_date:
        return []
    policy = get_policy_config()
    try:
        expiry = datetime.strptime(passport.expiry_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return []
    minimum = datetime.now(timezone.utc) + timedelta(
        days=policy.passport_min_validity_months_at_submission * 30
    )
    if expiry >= minimum:
        return []
    return [
        ValidationFinding(
            application_id=application.application_id,
            rule_id="passport_validity",
            rule_version=RULE_VERSION,
            result="fail",
            severity="overrideable_blocking",
            affected_field_or_document="passport.expiry_date",
            responsible_party="applicant",
            corrective_action=(
                "Passport must be valid at least "
                f"{policy.passport_min_validity_months_at_submission} months "
                "at submission, or a supervisor must approve a policy exception"
            ),
        )
    ]


def _ocr_mismatch_findings(
    db: Session, application: VisaApplication, applicant: Applicant, passport: Passport | None
) -> list[ValidationFinding]:
    documents = db.query(Document).filter_by(application_id=application.application_id).all()
    findings: list[ValidationFinding] = []
    for document in documents:
        result = (
            db.query(OcrResult)
            .filter_by(document_id=document.document_id)
            .order_by(OcrResult.ocr_result_id.desc())
            .first()
        )
        if result is None or result.extraction_status != "completed":
            continue
        values = {**result.extracted_fields, **result.reviewed_values}
        confirmed = bool(result.reviewed_values) or result.reviewer_id is not None

        for ocr_field, applicant_field in OCR_FIELD_TO_APPLICANT.items():
            extracted = values.get(ocr_field)
            entered = getattr(applicant, applicant_field, None)
            if extracted and entered and str(extracted) != str(entered) and not confirmed:
                findings.append(_mismatch_finding(application, f"applicant.{applicant_field}"))

        for ocr_field, passport_field in OCR_FIELD_TO_PASSPORT.items():
            extracted = values.get(ocr_field)
            entered = getattr(passport, passport_field, None) if passport else None
            if extracted and entered and str(extracted) != str(entered) and not confirmed:
                findings.append(_mismatch_finding(application, f"passport.{passport_field}"))
    return findings


def _mismatch_finding(application: VisaApplication, field_name: str) -> ValidationFinding:
    return ValidationFinding(
        application_id=application.application_id,
        rule_id="ocr_mismatch",
        rule_version=RULE_VERSION,
        result="fail",
        severity="overrideable_blocking",
        affected_field_or_document=field_name,
        responsible_party="applicant",
        corrective_action=(
            "Confirm the correct value or have an authorized officer record an override"
        ),
    )


def _duplicate_risk_findings(
    db: Session, application: VisaApplication, passport: Passport | None
) -> list[ValidationFinding]:
    if passport is None or not passport.passport_number:
        return []
    duplicate = (
        db.query(Passport)
        .join(VisaApplication, VisaApplication.application_id == Passport.application_id)
        .filter(
            Passport.passport_number == passport.passport_number,
            VisaApplication.application_id != application.application_id,
            VisaApplication.current_status.notin_(("abandoned", "rejected", "withdrawn", "closed")),
        )
        .first()
    )
    if duplicate is None:
        return []
    return [
        ValidationFinding(
            application_id=application.application_id,
            rule_id="duplicate_risk",
            rule_version=RULE_VERSION,
            result="fail",
            severity="warning",
            affected_field_or_document="passport.passport_number",
            responsible_party="sub_agency_officer",
            corrective_action="Confirm this is not a duplicate application before proceeding",
        )
    ]


def validate_application(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> ValidationOutcome:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="validation:run",
            owning_agency_id=(
                application.owning_sub_agency_id if identity.role != "applicant" else None
            ),
        )
    )

    applicant = db.get(Applicant, application.applicant_id)
    passport = db.query(Passport).filter_by(application_id=application_id).one_or_none()

    completeness = calculate_missing_items(application.visa_type, applicant, passport)
    findings: list[ValidationFinding] = []
    if not completeness.is_complete:
        required_field_gaps = [
            m for m in completeness.missing_items if not m.startswith("document.")
        ]
        if required_field_gaps:
            findings.append(
                ValidationFinding(
                    application_id=application_id,
                    rule_id="required_fields",
                    rule_version=RULE_VERSION,
                    result="fail",
                    severity="non_overrideable_blocking",
                    affected_field_or_document=",".join(required_field_gaps),
                    responsible_party="applicant",
                    corrective_action=(
                        "Complete all required applicant, passport, and consent fields"
                    ),
                )
            )

    findings.extend(_document_findings(db, application))
    findings.extend(_passport_validity_findings(application, passport))
    findings.extend(_ocr_mismatch_findings(db, application, applicant, passport))
    findings.extend(_duplicate_risk_findings(db, application, passport))

    for finding in findings:
        db.add(finding)
    db.flush()

    unresolved = _unresolved_blocking(findings)
    is_ready = len(unresolved) == 0

    if application.current_status == "documents_pending" and not any(
        f.rule_id == "document_presence" for f in unresolved
    ):
        result = transition(application.current_status, "ocr_and_validation")
        application.current_status = result.new_status
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=result.previous_status,
                new_status=result.new_status,
                source="documents_api",
                actor_or_service_id=identity.user_id,
                responsible_party=identity.role,
                next_action="Review OCR results and resolve validation findings",
                correlation_reference=correlation_reference,
            )
        )

    if application.current_status == "ocr_and_validation" and is_ready:
        result = transition(application.current_status, "ready_for_sub_agency_review")
        application.current_status = result.new_status
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=result.previous_status,
                new_status=result.new_status,
                source="documents_api",
                actor_or_service_id=identity.user_id,
                responsible_party=identity.role,
                next_action="Sub-agency wallet verification",
                correlation_reference=correlation_reference,
            )
        )

    db.commit()
    db.refresh(application)
    for finding in findings:
        db.refresh(finding)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.owning_sub_agency_id,
                action="application.validate",
                affected_case_or_record=application_id,
                outcome="ready" if is_ready else "blocking_findings_remain",
                source="documents_api",
                correlation_reference=correlation_reference,
            ),
        )

    if not is_ready:
        from src.notifications.notification_rules_engine import trigger_notification

        trigger_notification(db, application_id, "validation_failed", correlation_reference)

    return ValidationOutcome(
        findings=findings, current_status=application.current_status, is_ready=is_ready
    )
