"""Immigration processing adapter: received/under review/action
required/final decision (T133).

Mocked provider reads backend/tests/fixtures/integrations/immigration_processing.json.
"""

import json
from dataclasses import dataclass
from pathlib import Path

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "integrations"
    / "immigration_processing.json"
)

ACTION_REQUIRED_MARKER = "IMM_ACTION_REQUIRED"
REJECTED_MARKER = "IMM_REJECTED"
CONTRADICTORY_MARKER = "IMM_CONTRADICTORY"


@dataclass(frozen=True)
class ImmigrationUpdateResult:
    response_type: str  # action_required | final_decision | contradictory
    decision: str | None  # approved | rejected, only set when response_type == final_decision
    reason: str | None
    external_reference: str | None


def get_immigration_update(routing_signal: str) -> ImmigrationUpdateResult:
    fixture = json.loads(FIXTURE_PATH.read_text())

    if CONTRADICTORY_MARKER in routing_signal:
        return ImmigrationUpdateResult(
            response_type="contradictory",
            decision=None,
            reason="status_conflicts_with_case_history",
            external_reference=None,
        )
    if ACTION_REQUIRED_MARKER in routing_signal:
        response = fixture["action_required_response"]
        return ImmigrationUpdateResult(
            response_type="action_required",
            decision=None,
            reason=response["reason"],
            external_reference=None,
        )
    if REJECTED_MARKER in routing_signal:
        return ImmigrationUpdateResult(
            response_type="final_decision",
            decision="rejected",
            reason="eligibility_criteria_not_met",
            external_reference=None,
        )

    response = fixture["final_approved_response"]
    return ImmigrationUpdateResult(
        response_type="final_decision",
        decision="approved",
        reason=None,
        external_reference=response["external_reference"],
    )
