"""Wallet Ledger Event model (T090)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

EVENT_TYPES = ("balance_check", "reservation", "debit", "release", "refund", "reconciliation")


class WalletLedgerEvent(Base):
    __tablename__ = "wallet_ledger_events"

    wallet_event_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    agency_id: Mapped[str] = mapped_column(String(80), nullable=False)
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visa_applications.application_id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    fee_version: Mapped[str] = mapped_column(String(20), nullable=False)
    available_balance_result: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reservation_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    debit_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    release_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    refund_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    reconciliation_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
