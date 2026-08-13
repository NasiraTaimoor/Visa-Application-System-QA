"""Payment model (T129)."""

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

PAYMENT_STATES = (
    "required",
    "pending",
    "paid",
    "failed",
    "cancelled",
    "refunded",
    "disputed",
    "reconciled",
)


class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    payment_state: Mapped[str] = mapped_column(String(20), default="required", nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    fee_version: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    receipt_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    confirmation_source: Mapped[str | None] = mapped_column(String(60), nullable=True)
    reconciliation_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dispute_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    refund_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    finance_actor_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
