"""Submission model (sub-agency submission type) (T091)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Submission(Base):
    __tablename__ = "submissions"

    submission_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    submission_type: Mapped[str] = mapped_column(String(30), nullable=False)  # sub_agency | gdrfa
    source_agency_id: Mapped[str] = mapped_column(String(80), nullable=False)
    target_agency_or_system: Mapped[str] = mapped_column(String(80), nullable=False)
    snapshot_id: Mapped[str] = mapped_column(String(36), nullable=False)
    submission_reference: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="submitted", nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_response: Mapped[str | None] = mapped_column(String(200), nullable=True)
    response_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
