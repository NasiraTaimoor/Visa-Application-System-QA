"""GDRFA submission adapter: payload reference, submission attempt,
idempotency key (T112).

Mocked provider reads backend/tests/fixtures/integrations/gdrfa.json.
Scaffold-only markers on the snapshot id select a response variant.
"""

import json
import uuid
from dataclasses import dataclass
from pathlib import Path

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "integrations"
    / "gdrfa.json"
)

REJECT_MARKER = "GDRFA_REJECT"
TIMEOUT_MARKER = "GDRFA_TIMEOUT"
ACTION_REQUIRED_MARKER = "GDRFA_ACTION_REQUIRED"


@dataclass(frozen=True)
class GdrfaSubmissionResult:
    payload_reference: str
    response_type: str
    external_reference: str | None
    response_reason: str | None


def submit_to_gdrfa(routing_signal: str) -> GdrfaSubmissionResult:
    """`routing_signal` is any test-controllable string carried by the case
    (the scaffold uses the applicant's legal name, the way OCR/screening use
    content markers) so tests can select a mocked response variant without
    depending on server-generated identifiers."""
    fixture = json.loads(FIXTURE_PATH.read_text())
    payload_reference = f"gdrfa-payload-{uuid.uuid4()}"

    if REJECT_MARKER in routing_signal:
        response = fixture["rejection_response"]
    elif TIMEOUT_MARKER in routing_signal:
        response = fixture["timeout_response"]
    elif ACTION_REQUIRED_MARKER in routing_signal:
        response = fixture["action_required_response"]
    else:
        response = fixture["acknowledgement_response"]

    return GdrfaSubmissionResult(
        payload_reference=payload_reference,
        response_type=response["response_type"],
        external_reference=response.get("external_reference"),
        response_reason=response.get("response_reason"),
    )
