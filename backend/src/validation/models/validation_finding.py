"""Validation Finding model with severity classification (T068)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

SEVERITIES = (
    "informational",
    "warning",
    "blocking",
    "overrideable_blocking",
    "non_overrideable_blocking",
)


class ValidationFinding(Base):
    __tablename__ = "validation_findings"

    finding_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    rule_id: Mapped[str] = mapped_column(String(80), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # pass | fail
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    affected_field_or_document: Mapped[str | None] = mapped_column(String(120), nullable=True)
    responsible_party: Mapped[str | None] = mapped_column(String(60), nullable=True)
    corrective_action: Mapped[str | None] = mapped_column(String(300), nullable=True)
    override_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    override_actor_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    override_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
