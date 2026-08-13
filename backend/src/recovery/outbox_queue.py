"""Outbox queue and retry/dead-letter recovery queue (T022).

Mutating commands append an OutboxMessage in the same transaction as their
domain write; a worker (see backend/workers/outbox_worker.py) delivers each
message to its target (notification gateway, external submission, etc.) and
moves exhausted retries to the dead-letter state for support/recovery
visibility per integration-contracts.md failure handling rules.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.db.base import Base

MAX_ATTEMPTS_DEFAULT = 5


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    message_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    message_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload_reference: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=MAX_ATTEMPTS_DEFAULT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)


def enqueue(
    db: Session, message_id: str, message_type: str, payload_reference: str
) -> OutboxMessage:
    message = OutboxMessage(
        message_id=message_id, message_type=message_type, payload_reference=payload_reference
    )
    db.add(message)
    db.flush()
    return message


def record_attempt(
    db: Session, message: OutboxMessage, succeeded: bool, error: str | None = None
) -> OutboxMessage:
    message.attempt_count += 1
    message.last_attempt_at = datetime.now(timezone.utc)
    if succeeded:
        message.status = "delivered"
    elif message.attempt_count >= message.max_attempts:
        message.status = "dead_letter"
        message.last_error = error
    else:
        message.status = "retry_pending"
        message.last_error = error
    db.flush()
    return message
