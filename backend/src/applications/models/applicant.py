"""Applicant model (T040)."""

import uuid

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Applicant(Base):
    __tablename__ = "applicants"

    applicant_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    date_of_birth: Mapped[str | None] = mapped_column(String(10), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(60), nullable=True)
    contact_details: Mapped[dict] = mapped_column(JSON, default=dict)
    identity_references: Mapped[dict] = mapped_column(JSON, default=dict)
    sponsor_details: Mapped[dict] = mapped_column(JSON, default=dict)
    consent_records: Mapped[dict] = mapped_column(JSON, default=dict)
    agency_relationships: Mapped[list] = mapped_column(JSON, default=list)
    data_classification: Mapped[str] = mapped_column(
        String(30), default="restricted", nullable=False
    )
    retention_policy_id: Mapped[str] = mapped_column(String(60), default="applicant_identity_data")
