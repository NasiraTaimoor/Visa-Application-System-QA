"""Notification model (T146)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    recipient_category: Mapped[str] = mapped_column(String(40), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    preference_source: Mapped[str] = mapped_column(String(20), default="mandatory", nullable=False)
    message_classification: Mapped[str] = mapped_column(
        String(20), default="minimal", nullable=False
    )
    delivery_status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    retry_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
