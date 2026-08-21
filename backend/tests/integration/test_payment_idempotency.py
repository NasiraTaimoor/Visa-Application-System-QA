"""Duplicate payment callback preserves one financial outcome (T126).
Traceability: TS-FR-039/TC-FR-039, BR-027, E-015."""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_duplicate_payment_confirmation_preserves_single_outcome(client):
    application_id = _create_payment_pending_application(client)

    first = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    second = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["payment_state"] == second.json()["payment_state"] == "paid"

    from src.db.base import SessionLocal
    from src.finance.models.payment import Payment
    from src.finance.models.wallet_ledger_event import WalletLedgerEvent

    with SessionLocal() as db:
        payments = db.query(Payment).filter_by(application_id=application_id).all()
        assert len(payments) == 1
        debits = (
            db.query(WalletLedgerEvent)
            .filter_by(application_id=application_id, event_type="debit")
            .all()
        )
        assert len(debits) == 1
