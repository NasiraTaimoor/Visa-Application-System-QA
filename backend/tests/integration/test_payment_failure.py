"""Payment failure/dispute routes to finance review (T125). Traceability:
TS-FR-023/TC-FR-023, E-007."""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_payment_failure_moves_to_payment_failed_and_finance_can_reconcile(client):
    application_id = _create_payment_pending_application(client, legal_name="PAYMENT_FAIL Doe")

    failure = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert failure.json()["current_status"] == "payment_failed"

    reconcile = client.post(
        f"/api/v1/applications/{application_id}/payment/reconcile",
        json={
            "receipt_reference": "manual-recovery-0001",
            "amount": 5000,
            "currency": "AED",
            "reason": "confirmed via bank statement",
        },
        headers=auth_headers("finance_officer"),
    )
    assert reconcile.status_code == 200
    assert reconcile.json()["current_status"] == "paid"


def test_disputed_payment_keeps_case_pending_for_finance_review(client):
    application_id = _create_payment_pending_application(client, legal_name="PAYMENT_DISPUTE Doe")

    response = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["payment_state"] == "disputed"
    assert body["current_status"] == "payment_pending"
