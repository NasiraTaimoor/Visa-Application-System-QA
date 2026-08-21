"""Agency model and agency hierarchy/routing rules (T015)."""

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class Agency(Base):
    __tablename__ = "agencies"

    agency_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    agency_type: Mapped[str] = mapped_column(String(30), nullable=False)  # sub_agency | main_agency
    parent_agency_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    wallet_account_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    routing_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    permitted_roles: Mapped[list] = mapped_column(JSON, default=list)
