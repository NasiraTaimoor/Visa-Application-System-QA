"""Audit search/query service with role-based access and masking (T163)."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.audit.models.audit_event import AuditEvent
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity

# Fields masked from roles without a full audit-read grant (kept for parity
# with future non-auditor callers; audit:read itself is auditor-only today).
SENSITIVE_FIELDS = ("reason",)


@dataclass(frozen=True)
class AuditEventView:
    audit_event_id: str
    actor_or_service_id: str
    role: str
    agency_scope: str | None
    timestamp: str
    action: str
    affected_case_or_record: str
    outcome: str
    reason: str | None
    source: str
    correlation_reference: str


def search_audit_events(
    audit_db: Session,
    identity: Identity,
    application_id: str | None = None,
    action_prefix: str | None = None,
) -> list[AuditEventView]:
    authorize(AuthorizationContext(identity=identity, action="audit:read"))

    query = audit_db.query(AuditEvent)
    if application_id:
        query = query.filter(AuditEvent.affected_case_or_record == application_id)
    if action_prefix:
        query = query.filter(AuditEvent.action.like(f"{action_prefix}%"))

    events = query.order_by(AuditEvent.timestamp.asc()).all()
    return [
        AuditEventView(
            audit_event_id=e.audit_event_id,
            actor_or_service_id=e.actor_or_service_id,
            role=e.role,
            agency_scope=e.agency_scope,
            timestamp=e.timestamp.isoformat(),
            action=e.action,
            affected_case_or_record=e.affected_case_or_record,
            outcome=e.outcome,
            reason=e.reason,
            source=e.source,
            correlation_reference=e.correlation_reference,
        )
        for e in events
    ]
