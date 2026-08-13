"""Consent and Retention Policy model and base policy enforcement (T024)."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.db.base import Base


class ConsentRetentionPolicy(Base):
    __tablename__ = "consent_retention_policies"

    policy_id: Mapped[str] = mapped_column(String(60), primary_key=True)
    data_category: Mapped[str] = mapped_column(String(80), nullable=False)
    lawful_basis: Mapped[str] = mapped_column(String(120), nullable=False)
    consent_required: Mapped[bool] = mapped_column(default=True, nullable=False)
    retention_period_days: Mapped[int] = mapped_column(nullable=False)
    deletion_path: Mapped[str] = mapped_column(String(200), nullable=False)
    anonymisation_path: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_hold_behavior: Mapped[str] = mapped_column(String(200), nullable=False)
    production_test_data_rules: Mapped[str] = mapped_column(String(300), nullable=False)
    effective_from: Mapped[str] = mapped_column(String(10), nullable=False)
    effective_to: Mapped[str | None] = mapped_column(String(10), nullable=True)


def enforce_policy_exists(db: Session, policy_id: str) -> ConsentRetentionPolicy:
    """A data category may not be introduced for production use without a
    documented policy (constitution: Data Protection and Compliance)."""
    policy = db.get(ConsentRetentionPolicy, policy_id)
    if policy is None:
        raise ValueError(f"no consent/retention policy documented for '{policy_id}'")
    return policy


DEFAULT_POLICIES = [
    ConsentRetentionPolicy(
        policy_id="applicant_identity_data",
        data_category="applicant_identity",
        lawful_basis="consent_and_legal_processing",
        consent_required=True,
        retention_period_days=2555,
        deletion_path="scheduled_purge_after_retention",
        anonymisation_path="anonymise_on_legal_hold_release",
        legal_hold_behavior="retain_until_hold_released",
        production_test_data_rules="synthetic_only_in_non_production",
        effective_from="2026-08-11",
    ),
    ConsentRetentionPolicy(
        policy_id="abandoned_draft_data",
        data_category="draft_application",
        lawful_basis="consent",
        consent_required=True,
        retention_period_days=90,
        deletion_path="scheduled_purge_after_retention",
        anonymisation_path="anonymise_on_abandon",
        legal_hold_behavior="retain_until_hold_released",
        production_test_data_rules="synthetic_only_in_non_production",
        effective_from="2026-08-11",
    ),
]
