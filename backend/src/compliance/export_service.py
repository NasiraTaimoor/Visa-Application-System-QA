"""Compliance export service with audited export events (T164)."""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.audit_search_service import AuditEventView, search_audit_events
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity


class ReasonRequiredError(ValueError):
    pass


@dataclass(frozen=True)
class ExportResult:
    export_reference: str
    record_count: int
    records: list[AuditEventView]


def export_records(
    audit_db: Session,
    identity: Identity,
    application_id: str | None,
    business_reason: str,
    correlation_reference: str,
) -> ExportResult:
    if not business_reason:
        raise ReasonRequiredError("a business reason is required for compliance export")

    authorize(
        AuthorizationContext(
            identity=identity,
            action="audit:export",
            business_reason=business_reason,
            requires_reason=True,
        )
    )

    records = search_audit_events(audit_db, identity, application_id=application_id)
    export_reference = f"EXPORT-{uuid.uuid4().hex[:12].upper()}"

    record_audit_event(
        audit_db,
        AuditEventInput(
            actor_or_service_id=identity.user_id,
            role=identity.role,
            action="compliance.export",
            affected_case_or_record=application_id or "multiple",
            outcome="success",
            reason=business_reason,
            source="audit_api",
            correlation_reference=correlation_reference,
            metadata_reference=export_reference,
        ),
    )

    return ExportResult(
        export_reference=export_reference, record_count=len(records), records=records
    )
