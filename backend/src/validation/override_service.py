"""Override approval handling for overrideable blocking findings (T074).

BR-004/BR-015: only "overrideable_blocking" findings may be bypassed, and
only with an elevated role and a recorded reason (E-013).
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.validation.models.validation_finding import ValidationFinding


class FindingNotFoundError(ValueError):
    pass


class NonOverrideableFindingError(ValueError):
    pass


@dataclass(frozen=True)
class ApproveOverrideCommand:
    finding_id: str
    reason: str
    correlation_reference: str


def approve_override(
    db: Session, identity: Identity, owning_agency_id: str, cmd: ApproveOverrideCommand
) -> ValidationFinding:
    if not cmd.reason:
        raise ValueError("an override reason is required")

    authorize(
        AuthorizationContext(
            identity=identity,
            action="validation:override_approve",
            business_reason=cmd.reason,
            requires_reason=True,
        )
    )

    finding = db.get(ValidationFinding, cmd.finding_id)
    if finding is None:
        raise FindingNotFoundError(cmd.finding_id)

    if finding.severity != "overrideable_blocking":
        raise NonOverrideableFindingError(
            f"finding severity '{finding.severity}' cannot be overridden"
        )

    finding.override_status = "approved"
    finding.override_actor_id = identity.user_id
    finding.override_reason = cmd.reason
    finding.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(finding)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=owning_agency_id,
                action="validation.override_approve",
                affected_case_or_record=finding.application_id,
                outcome="success",
                reason=cmd.reason,
                source="documents_api",
                correlation_reference=cmd.correlation_reference,
                metadata_reference=finding.finding_id,
            ),
        )

    return finding
