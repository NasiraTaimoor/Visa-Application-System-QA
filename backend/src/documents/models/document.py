"""Document model with versioning and retention classification (T066)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(60), nullable=False)
    file_reference: Mapped[str] = mapped_column(String(300), nullable=False)
    file_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    upload_actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    upload_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    upload_status: Mapped[str] = mapped_column(String(30), default="uploaded", nullable=False)
    screening_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(30), default="unverified", nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    replaced_document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    retention_classification: Mapped[str] = mapped_column(
        String(30), default="standard", nullable=False
    )
