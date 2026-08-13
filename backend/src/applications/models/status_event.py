"""Status Event model (T017)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class StatusEvent(Base):
    __tablename__ = "status_events"

    status_event_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    previous_status: Mapped[str | None] = mapped_column(String(60), nullable=True)
    new_status: Mapped[str] = mapped_column(String(60), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    actor_or_service_id: Mapped[str] = mapped_column(String(120), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    responsible_party: Mapped[str | None] = mapped_column(String(80), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    next_action: Mapped[str | None] = mapped_column(String(200), nullable=True)
    visibility_classification: Mapped[str] = mapped_column(
        String(30), default="standard", nullable=False
    )
    correlation_reference: Mapped[str] = mapped_column(String(120), nullable=False)
