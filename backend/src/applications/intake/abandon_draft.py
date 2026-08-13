"""Abandon draft command per retention rules (T047)."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import InvalidTransitionError
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.compliance.models.consent_retention_policy import enforce_policy_exists

ABANDONABLE_STATUSES = frozenset({"draft_created", "documents_pending", "ocr_and_validation"})


class DraftNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class AbandonDraftCommand:
    application_id: str
    reason: str
    correlation_reference: str


def abandon_draft(db: Session, identity: Identity, cmd: AbandonDraftCommand) -> VisaApplication:
    application = db.get(VisaApplication, cmd.application_id)
    if application is None:
        raise DraftNotFoundError(cmd.application_id)

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

    if application.current_status not in ABANDONABLE_STATUSES:
        raise InvalidTransitionError(application.current_status, "abandoned")

    # Raises if no retention policy is documented for this data category; the
    # policy itself is applied by a real purge job, not read here.
    enforce_policy_exists(db, "abandoned_draft_data")

    application.current_status = "abandoned"
    db.commit()
    db.refresh(application)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.owning_sub_agency_id,
                action="application.abandon",
                affected_case_or_record=application.application_id,
                outcome="success",
                reason=cmd.reason,
                source="applications_api",
                correlation_reference=cmd.correlation_reference,
            ),
        )

    return application
