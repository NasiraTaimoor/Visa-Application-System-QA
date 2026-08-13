"""Visa Application core model and lifecycle status field (T016)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class VisaApplication(Base):
    __tablename__ = "visa_applications"

    application_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_reference: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    applicant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applicants.applicant_id"), nullable=False
    )
    visa_type: Mapped[str] = mapped_column(String(40), nullable=False)
    owning_sub_agency_id: Mapped[str] = mapped_column(String(80), nullable=False)
    routed_main_agency_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    current_status: Mapped[str] = mapped_column(String(60), default="draft_created", nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    validated_snapshot_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    fee_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
    terminal_outcome: Mapped[str | None] = mapped_column(String(30), nullable=True)
    terminal_locked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    readiness_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    readiness_approved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
