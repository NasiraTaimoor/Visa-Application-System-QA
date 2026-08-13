"""Payment provider adapter: initiation, confirmation, receipt, dispute,
refund (T130).

Mocked provider reads backend/tests/fixtures/integrations/payment_provider.json.
Uses the same test-controllable routing-signal marker pattern as the OCR,
screening, and GDRFA adapters.
"""

import json
from dataclasses import dataclass
from pathlib import Path

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "integrations"
    / "payment_provider.json"
)

FAIL_MARKER = "PAYMENT_FAIL"
DISPUTE_MARKER = "PAYMENT_DISPUTE"


@dataclass(frozen=True)
class PaymentConfirmationResult:
    state: str  # paid | failed | disputed
    provider_reference: str | None
    receipt_reference: str | None
    reason: str | None


def confirm_payment(routing_signal: str) -> PaymentConfirmationResult:
    fixture = json.loads(FIXTURE_PATH.read_text())

    if DISPUTE_MARKER in routing_signal:
        return PaymentConfirmationResult(
            state="disputed",
            provider_reference=None,
            receipt_reference=None,
            reason="payment_disputed_by_cardholder",
        )
    if FAIL_MARKER in routing_signal:
        response = fixture["failed_response"]
        return PaymentConfirmationResult(
            state=response["state"],
            provider_reference=None,
            receipt_reference=None,
            reason=response["reason"],
        )

    response = fixture["paid_response"]
    return PaymentConfirmationResult(
        state=response["state"],
        provider_reference=response["provider_reference"],
        receipt_reference=response["receipt_reference"],
        reason=None,
    )
