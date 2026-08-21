"""Error Record model and base recovery task service (T023).

User-facing messages must be safe (no secrets/stack traces/tokens/internal
endpoints) per data-model.md; the protected diagnostic reference is the only
place detail is retained, for support/engineering follow-up.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.db.base import Base


class ErrorRecord(Base):
    __tablename__ = "error_records"

    error_record_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source_component: Mapped[str] = mapped_column(String(80), nullable=False)
    error_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    user_safe_message: Mapped[str] = mapped_column(String(300), nullable=False)
    protected_diagnostic_reference: Mapped[str] = mapped_column(String(120), nullable=False)
    recovery_owner: Mapped[str] = mapped_column(String(60), nullable=False)
    recovery_status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    correlation_reference: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def record_error(
    db: Session,
    *,
    application_id: str | None,
    source_component: str,
    error_type: str,
    severity: str,
    user_safe_message: str,
    protected_diagnostic_reference: str,
    recovery_owner: str,
    correlation_reference: str,
) -> ErrorRecord:
    record = ErrorRecord(
        application_id=application_id,
        source_component=source_component,
        error_type=error_type,
        severity=severity,
        user_safe_message=user_safe_message,
        protected_diagnostic_reference=protected_diagnostic_reference,
        recovery_owner=recovery_owner,
        correlation_reference=correlation_reference,
    )
    db.add(record)
    db.flush()
    return record


def resolve_error(db: Session, error_record_id: str) -> ErrorRecord:
    record = db.get(ErrorRecord, error_record_id)
    if record is None:
        raise ValueError("error record not found")
    record.recovery_status = "resolved"
    record.resolved_at = datetime.now(timezone.utc)
    db.flush()
    return record
