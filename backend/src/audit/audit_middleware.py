"""Mandatory audit field validation and audit-write middleware (T020).

`record_audit_event` is the single append-only entry point every mutating
command in this codebase must call. It validates the mandatory fields from
data-model.md before writing, and computes a tamper-evidence marker (a hash
chained implementation is a real-environment upgrade; the scaffold uses a
deterministic content hash so tests can assert integrity).
"""

import hashlib
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.audit.models.audit_event import AuditEvent

REQUIRED_FIELDS = (
    "actor_or_service_id",
    "role",
    "action",
    "affected_case_or_record",
    "outcome",
    "source",
    "correlation_reference",
)


class AuditFieldMissingError(ValueError):
    pass


@dataclass
class AuditEventInput:
    actor_or_service_id: str
    role: str
    action: str
    affected_case_or_record: str
    outcome: str
    source: str
    correlation_reference: str
    agency_scope: str | None = None
    reason: str | None = None
    metadata_reference: str | None = None


def _tamper_marker(event: AuditEventInput) -> str:
    payload = "|".join(
        [
            event.actor_or_service_id,
            event.role,
            event.action,
            event.affected_case_or_record,
            event.outcome,
            event.source,
            event.correlation_reference,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_audit_event(db: Session, event: AuditEventInput) -> AuditEvent:
    for field_name in REQUIRED_FIELDS:
        if not getattr(event, field_name):
            raise AuditFieldMissingError(f"missing required audit field: {field_name}")

    row = AuditEvent(
        actor_or_service_id=event.actor_or_service_id,
        role=event.role,
        agency_scope=event.agency_scope,
        action=event.action,
        affected_case_or_record=event.affected_case_or_record,
        outcome=event.outcome,
        reason=event.reason,
        source=event.source,
        correlation_reference=event.correlation_reference,
        metadata_reference=event.metadata_reference,
        tamper_evidence_marker=_tamper_marker(event),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
