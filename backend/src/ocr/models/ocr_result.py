"""OCR Result model (T067)."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class OcrResult(Base):
    __tablename__ = "ocr_results"

    ocr_result_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.document_id"), nullable=False
    )
    extraction_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    extracted_fields: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence_by_field: Mapped[dict] = mapped_column(JSON, default=dict)
    overall_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    warning_flags: Mapped[list] = mapped_column(JSON, default=list)
    reviewed_values: Mapped[dict] = mapped_column(JSON, default=dict)
    reviewer_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    correction_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    source_payload_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
