"""Passport intake-fields model (T041)."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Passport(Base):
    __tablename__ = "passports"

    passport_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    passport_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    issuing_country: Mapped[str | None] = mapped_column(String(60), nullable=True)
    issue_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    expiry_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    machine_readable_details: Mapped[dict] = mapped_column(JSON, default=dict)
    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    confirmed_source: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )  # applicant | ocr_review
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
