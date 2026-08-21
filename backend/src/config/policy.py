"""Environment/policy configuration (T006).

Centralizes the configurable business policy referenced across services:
visa types, document requirements, fee schedules, passport validity policy,
agency hierarchy, routing rules, notification rules, retention policy, and
the action-level permission matrix. Values here are scaffold defaults drawn
from spec.md / data-model.md and are safe to override per environment.
"""

from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(frozen=True)
class PolicyConfig:
    visa_types: tuple[str, ...] = (
        "tourist",
        "work",
        "student",
        "family_sponsorship",
        "transit",
    )

    # document_type -> required for visa types (subset shown; extend per policy)
    document_requirements: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "passport_bio_page": ("tourist", "work", "student", "family_sponsorship", "transit"),
            "photo": ("tourist", "work", "student", "family_sponsorship", "transit"),
            "sponsor_letter": ("family_sponsorship",),
            "enrollment_letter": ("student",),
            "employment_offer": ("work",),
        }
    )

    # visa_type -> stage -> fee amount (minor currency units), fee_version bumps on change
    fee_schedule_version: str = "2026.1"
    fee_schedule: dict[str, dict[str, int]] = field(
        default_factory=lambda: {
            "tourist": {"sub_agency_submission": 5000, "immigration_processing": 20000},
            "work": {"sub_agency_submission": 8000, "immigration_processing": 45000},
            "student": {"sub_agency_submission": 6000, "immigration_processing": 30000},
            "family_sponsorship": {"sub_agency_submission": 7000, "immigration_processing": 35000},
            "transit": {"sub_agency_submission": 2000, "immigration_processing": 8000},
        }
    )
    fee_currency: str = "AED"

    passport_min_validity_months_at_submission: int = 6

    ocr_confidence_warning_threshold: float = 0.85
    ocr_confidence_blocking_threshold: float = 0.60

    # BR-020 baseline document limits.
    document_max_size_bytes: int = 10 * 1024 * 1024
    document_max_pages: int = 20
    document_allowed_extensions: tuple[str, ...] = (".pdf", ".jpg", ".jpeg", ".png")
    ocr_eligible_document_types: tuple[str, ...] = ("passport_bio_page",)

    # agency_id -> parent_agency_id (None for main/root agencies)
    agency_hierarchy: dict[str, str | None] = field(
        default_factory=lambda: {
            "main-agency-root": None,
            "sub-agency-001": "main-agency-root",
            "sub-agency-002": "main-agency-root",
        }
    )

    notification_events: tuple[str, ...] = (
        "submission_created",
        "correction_requested",
        "validation_failed",
        "wallet_shortfall",
        "payment_outcome",
        "gdrfa_response",
        "immigration_event",
        "final_decision",
    )
    mandatory_notification_events: tuple[str, ...] = (
        "correction_requested",
        "final_decision",
        "wallet_shortfall",
    )

    retention_period_days_default: int = 2555  # ~7 years
    retention_period_days_abandoned_draft: int = 90

    notification_retry_limit: int = 5

    # role -> allowed action keys (coarse scaffold matrix; refined per module)
    permission_matrix: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "applicant": (
                "intake:write_own",
                "document:upload_own",
                "document:replace_own",
                "ocr:review_confirm",
                "validation:run",
                "status:read_own",
            ),
            "sub_agency_officer": (
                "intake:write_own_agency",
                "document:upload_own_agency",
                "document:replace_own_agency",
                "ocr:review_confirm",
                "validation:run",
                "wallet:verify",
                "submission:submit_main_agency",
                "status:read_own_agency",
            ),
            "sub_agency_admin": (
                "intake:write_own_agency",
                "ocr:review_confirm",
                "validation:run",
                "wallet:verify",
                "submission:submit_main_agency",
                "status:read_own_agency",
                "agency:manage_users",
            ),
            "main_agency_case_officer": (
                "case:process",
                "case:correction_request",
                "case:reject",
                "case:readiness_approve",
                "gdrfa:submit",
                "status:read_routed",
            ),
            "main_agency_supervisor": (
                "case:process",
                "case:escalate",
                "case:readiness_approve",
                "validation:override_approve",
                "gdrfa:submit",
                "immigration:record_update",
                "status:read_routed",
            ),
            "finance_officer": (
                "payment:record",
                "payment:reconcile",
                "wallet:reconcile",
                "status:read_financial",
            ),
            "gdrfa_immigration_liaison": (
                "gdrfa:respond",
                "immigration:record_update",
                "status:read_routed",
            ),
            "support_admin": (
                "recovery:read",
                "recovery:resolve",
                "case:search_masked",
                "audit:access_reason_required",
            ),
            "auditor_compliance": ("audit:read", "audit:export"),
            "system_service": (
                "integration:callback",
                "notification:deliver",
                "monitoring:emit",
                "immigration:record_update",
                "payment:record",
            ),
        }
    )


@lru_cache
def get_policy_config() -> PolicyConfig:
    return PolicyConfig()
