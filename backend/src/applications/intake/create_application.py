"""Create application command: scope/consent check, single draft, single
audit event (T044)."""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.idempotency.idempotency_store import DuplicateRequestReplay, claim_or_replay
from src.applications.intake.consent_service import capture_consent
from src.applications.models.applicant import Applicant
from src.applications.models.visa_application import VisaApplication
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity


@dataclass(frozen=True)
class CreateApplicationCommand:
    visa_type: str
    owning_sub_agency_id: str
    consent_given: bool
    correlation_reference: str
    idempotency_key: str | None = None
    legal_name: str | None = None


def _next_case_reference(db: Session) -> str:
    count = db.query(VisaApplication).count()
    return f"VA-{count + 1:06d}"


def create_application(
    db: Session, identity: Identity, cmd: CreateApplicationCommand
) -> VisaApplication:
    authorize(
        AuthorizationContext(
            identity=identity,
            action=(
                "intake:write_own" if identity.role == "applicant" else "intake:write_own_agency"
            ),
            owning_agency_id=cmd.owning_sub_agency_id if identity.role != "applicant" else None,
        )
    )

    # Idempotency protects retries of the *same* client request; without an
    # explicit caller-supplied key (e.g. a client-generated request nonce)
    # each call is a distinct new-draft request, per api-contract.md.
    idempotency_key = cmd.idempotency_key or f"create_application:{uuid.uuid4()}"
    application_id = str(uuid.uuid4())
    try:
        claim_or_replay(
            db, idempotency_key, scope="create_application", result_reference=application_id
        )
    except DuplicateRequestReplay as replay:
        existing = db.get(VisaApplication, replay.existing_result_reference)
        if existing is not None:
            return existing
        raise

    applicant = Applicant(legal_name=cmd.legal_name)
    capture_consent(db, applicant, cmd.consent_given)
    db.add(applicant)
    db.flush()

    application = VisaApplication(
        application_id=application_id,
        case_reference=_next_case_reference(db),
        applicant_id=applicant.applicant_id,
        visa_type=cmd.visa_type,
        owning_sub_agency_id=cmd.owning_sub_agency_id,
        current_status="draft_created",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=cmd.owning_sub_agency_id,
                action="application.create",
                affected_case_or_record=application.application_id,
                outcome="success",
                source="applications_api",
                correlation_reference=cmd.correlation_reference,
            ),
        )

    return application
