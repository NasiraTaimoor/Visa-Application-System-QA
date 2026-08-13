"""Audit Event model and append-only write path (T019).

Mandatory fields per data-model.md: actor/service identity, role, agency
scope, timestamp, action, affected case/record, result, reason (where
applicable), source, correlation reference. Ordinary users cannot modify or
delete audit records — no update/delete helpers are exposed here.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.audit.store.base import AuditBase


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AuditEvent(AuditBase):
    __tablename__ = "audit_events"

    audit_event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    actor_or_service_id: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(60), nullable=False)
    agency_scope: Mapped[str | None] = mapped_column(String(80), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False
    )
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    affected_case_or_record: Mapped[str] = mapped_column(String(120), nullable=False)
    outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    correlation_reference: Mapped[str] = mapped_column(String(120), nullable=False)
    metadata_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tamper_evidence_marker: Mapped[str] = mapped_column(String(64), nullable=False)
