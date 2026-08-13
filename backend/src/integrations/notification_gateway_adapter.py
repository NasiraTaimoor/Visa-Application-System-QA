"""Notification gateway adapter with delivery attempt/result/retry tracking
(T148). Mocked gateway reads
backend/tests/fixtures/integrations/notification_gateway.json. Uses the
`NOTIFY_FAIL` marker (via the same test-controllable routing-signal pattern
as the other adapters) to force delivery failure for retry-exhaustion tests.
"""

import json
from dataclasses import dataclass
from pathlib import Path

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "integrations"
    / "notification_gateway.json"
)

FAIL_MARKER = "NOTIFY_FAIL"


@dataclass(frozen=True)
class DeliveryAttemptResult:
    delivered: bool
    failure_reason: str | None


def attempt_delivery(routing_signal: str) -> DeliveryAttemptResult:
    fixture = json.loads(FIXTURE_PATH.read_text())
    if FAIL_MARKER in routing_signal:
        response = fixture["failed_response"]
        return DeliveryAttemptResult(delivered=False, failure_reason=response["failure_reason"])
    return DeliveryAttemptResult(delivered=True, failure_reason=None)
