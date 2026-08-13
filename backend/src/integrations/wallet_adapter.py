"""Wallet/ledger provider adapter: available-balance checks, reservation,
debit, release, refund, and reconciliation references (T093).

Mocked provider reads backend/tests/fixtures/integrations/wallet_ledger.json
for each sub-agency's starting balance. Available balance (BR-007) excludes
amounts already reserved, debited, disputed, or legally held: it is the
fixture starting balance minus the net of this agency's own ledger events
recorded so far, which is why the calculation lives alongside the mocked
provider rather than purely in the fixture.
"""

import json
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.finance.models.wallet_ledger_event import WalletLedgerEvent

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "integrations"
    / "wallet_ledger.json"
)

# Ledger events that reduce currently-available balance until released/refunded.
ENCUMBERING_EVENT_TYPES = ("reservation", "debit")
RELEASING_EVENT_TYPES = ("release", "refund")


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def starting_balance(agency_id: str) -> int:
    fixture = _load_fixture()
    return fixture["agency_balances"].get(agency_id, 0)


def available_balance(db: Session, agency_id: str) -> int:
    encumbered = (
        db.query(func.coalesce(func.sum(WalletLedgerEvent.amount), 0))
        .filter(
            WalletLedgerEvent.agency_id == agency_id,
            WalletLedgerEvent.event_type.in_(ENCUMBERING_EVENT_TYPES),
            WalletLedgerEvent.status == "active",
        )
        .scalar()
    )
    return starting_balance(agency_id) - int(encumbered or 0)
