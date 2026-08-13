"""External Case Response model (T108)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class ExternalCaseResponse(Base):
    __tablename__ = "external_case_responses"

    response_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    source_system: Mapped[str] = mapped_column(
        String(40), nullable=False
    )  # gdrfa | payment | immigration
    external_reference: Mapped[str] = mapped_column(String(120), nullable=False)
    response_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status_value: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    payload_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    matched_status: Mapped[str] = mapped_column(String(20), default="unmatched", nullable=False)
    quarantine_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
