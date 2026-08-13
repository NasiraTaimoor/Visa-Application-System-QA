"""Lifecycle workflow state machine (T018).

Enforces the spec's status transition matrix (plan.md "Application Lifecycle
Workflow"). Invalid transitions raise without mutating case data; the caller
is responsible for actually persisting `new_status` only after `transition`
succeeds and for writing the paired StatusEvent + AuditEvent.
"""

from dataclasses import dataclass

TERMINAL_STATUSES = frozenset(
    {"approved", "rejected", "cancelled", "withdrawn", "expired", "closed"}
)

# state -> set of allowed next states, per plan.md's 11-stage lifecycle plus
# rework/correction loops described in data-model.md.
TRANSITIONS: dict[str, frozenset[str]] = {
    "draft_created": frozenset({"documents_pending", "abandoned"}),
    "documents_pending": frozenset({"ocr_and_validation", "abandoned"}),
    "ocr_and_validation": frozenset(
        {"documents_pending", "ready_for_sub_agency_review", "abandoned"}
    ),
    "ready_for_sub_agency_review": frozenset({"documents_pending", "wallet_verified", "abandoned"}),
    "wallet_verified": frozenset({"ready_for_sub_agency_review", "submitted_to_main_agency"}),
    "submitted_to_main_agency": frozenset({"main_agency_processing"}),
    "main_agency_processing": frozenset({"correction_requested", "gdrfa_submitted", "rejected"}),
    "correction_requested": frozenset({"main_agency_processing"}),
    "gdrfa_submitted": frozenset({"correction_requested", "payment_pending", "rejected"}),
    "payment_pending": frozenset({"paid", "payment_failed"}),
    "payment_failed": frozenset({"payment_pending", "cancelled"}),
    "paid": frozenset({"immigration_processing"}),
    "immigration_processing": frozenset(
        {
            "approved",
            "rejected",
            "cancelled",
            "withdrawn",
            "expired",
            "closed",
            "correction_requested",
        }
    ),
    "abandoned": frozenset(),
    "approved": frozenset({"closed"}),
    "rejected": frozenset({"closed"}),
    "cancelled": frozenset({"closed"}),
    "withdrawn": frozenset({"closed"}),
    "expired": frozenset({"closed"}),
    "closed": frozenset(),
}


class InvalidTransitionError(ValueError):
    def __init__(self, current: str, target: str):
        super().__init__(f"transition from '{current}' to '{target}' is not permitted")
        self.current = current
        self.target = target


@dataclass(frozen=True)
class TransitionResult:
    previous_status: str
    new_status: str
    is_terminal: bool


def is_terminal(status: str) -> bool:
    return status in TERMINAL_STATUSES


def transition(current_status: str, target_status: str) -> TransitionResult:
    if is_terminal(current_status) and target_status not in TRANSITIONS.get(
        current_status, frozenset()
    ):
        raise InvalidTransitionError(current_status, target_status)
    allowed = TRANSITIONS.get(current_status, frozenset())
    if target_status not in allowed:
        raise InvalidTransitionError(current_status, target_status)
    return TransitionResult(
        previous_status=current_status,
        new_status=target_status,
        is_terminal=is_terminal(target_status),
    )
