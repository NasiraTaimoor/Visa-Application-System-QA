"""Readiness approval and escalation service (T111).

Readiness approval does not itself change lifecycle status: per the status
transition matrix, `main_agency_processing -> gdrfa_submitted` requires
readiness approval *and* satisfied prerequisites, checked together at GDRFA
submission time (gdrfa_response_service / GDRFA submission route).
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.applications.models.visa_application import VisaApplication
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity


class ApplicationNotFoundError(ValueError):
    pass


class InvalidReadinessStateError(ValueError):
    pass


class ReasonRequiredError(ValueError):
    pass


@dataclass(frozen=True)
class ApproveReadinessCommand:
    application_id: str
    reason: str
    correlation_reference: str


def approve_readiness(
    db: Session, identity: Identity, cmd: ApproveReadinessCommand
) -> VisaApplication:
    if not cmd.reason:
        raise ReasonRequiredError("a readiness decision reason is required")

    application = db.get(VisaApplication, cmd.application_id)
    if application is None:
        raise ApplicationNotFoundError(cmd.application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="case:readiness_approve",
            owning_agency_id=application.routed_main_agency_id,
            business_reason=cmd.reason,
            requires_reason=True,
        )
    )

    if application.current_status != "main_agency_processing":
        raise InvalidReadinessStateError(
            "readiness can only be approved while status is 'main_agency_processing', "
            f"case is '{application.current_status}'"
        )

    application.readiness_approved_at = datetime.now(timezone.utc)
    application.readiness_approved_by = identity.user_id
    db.commit()
    db.refresh(application)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.routed_main_agency_id,
                action="case.readiness_approve",
                affected_case_or_record=cmd.application_id,
                outcome="success",
                reason=cmd.reason,
                source="main_agency_api",
                correlation_reference=cmd.correlation_reference,
            ),
        )

    return application
