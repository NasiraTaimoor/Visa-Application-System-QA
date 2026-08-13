"""Idempotency key store and idempotent-command handling (T021).

Business-reference idempotency per research.md: submissions, wallet events,
payments, integrations, and notifications key on a stable business
reference so duplicate clicks, retries, and concurrent attempts produce
exactly one accepted outcome.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.db.base import Base


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    idempotency_key: Mapped[str] = mapped_column(String(150), primary_key=True)
    scope: Mapped[str] = mapped_column(String(60), nullable=False)
    result_reference: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class DuplicateRequestReplay(Exception):
    """Raised (informationally) when a caller should return the prior result
    rather than re-executing a mutating command."""

    def __init__(self, existing_result_reference: str):
        super().__init__("idempotent replay: returning existing result")
        self.existing_result_reference = existing_result_reference


def get_existing(db: Session, idempotency_key: str, scope: str) -> IdempotencyRecord | None:
    return (
        db.query(IdempotencyRecord)
        .filter_by(idempotency_key=idempotency_key, scope=scope)
        .one_or_none()
    )


def claim_or_replay(
    db: Session, idempotency_key: str, scope: str, result_reference: str
) -> IdempotencyRecord:
    """Call once the business outcome is known and about to be persisted, or
    ahead of a side-effecting external call keyed by the same reference."""
    existing = get_existing(db, idempotency_key, scope)
    if existing is not None:
        raise DuplicateRequestReplay(existing.result_reference)
    record = IdempotencyRecord(
        idempotency_key=idempotency_key, scope=scope, result_reference=result_reference
    )
    db.add(record)
    db.flush()
    return record
