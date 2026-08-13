"""Update intake command: save applicant/contact/passport/travel/sponsor/
visa/consent fields with optimistic-concurrency versioning (T045)."""

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from src.applications.intake.completeness_service import (
    CompletenessResult,
    calculate_missing_items,
    get_accepted_document_types,
)
from src.applications.models.applicant import Applicant
from src.applications.models.passport import Passport
from src.applications.models.visa_application import VisaApplication
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity


class VersionConflictError(ValueError):
    pass


class ApplicationNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class UpdateIntakeCommand:
    application_id: str
    expected_version: int
    correlation_reference: str
    applicant_fields: dict = field(default_factory=dict)
    passport_fields: dict = field(default_factory=dict)


def update_intake(
    db: Session, identity: Identity, cmd: UpdateIntakeCommand
) -> tuple[VisaApplication, CompletenessResult]:
    application = db.get(VisaApplication, cmd.application_id)
    if application is None:
        raise ApplicationNotFoundError(cmd.application_id)

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

    if application.current_version != cmd.expected_version:
        raise VersionConflictError(
            f"expected version {cmd.expected_version}, "
            f"current version is {application.current_version}"
        )

    applicant = db.get(Applicant, application.applicant_id)
    for key, value in cmd.applicant_fields.items():
        if hasattr(applicant, key):
            setattr(applicant, key, value)

    passport = db.query(Passport).filter_by(application_id=application.application_id).one_or_none()
    if cmd.passport_fields:
        if passport is None:
            passport = Passport(application_id=application.application_id)
            db.add(passport)
        for key, value in cmd.passport_fields.items():
            if hasattr(passport, key):
                setattr(passport, key, value)

    application.current_version += 1
    db.commit()
    db.refresh(application)

    accepted_document_types = get_accepted_document_types(db, application.application_id)
    completeness = calculate_missing_items(
        application.visa_type, applicant, passport, accepted_document_types
    )

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.owning_sub_agency_id,
                action="application.update_intake",
                affected_case_or_record=application.application_id,
                outcome="success",
                source="applications_api",
                correlation_reference=cmd.correlation_reference,
            ),
        )

    return application, completeness
