from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_manual_reconciliation_requires_finance_role(client):
    application_id = _create_payment_pending_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/payment/reconcile",
        json={
            "receipt_reference": "manual-0001",
            "amount": 5000,
            "currency": "AED",
            "reason": "bank transfer confirmed",
        },
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 403


def test_manual_reconciliation_moves_case_to_paid(client):
    application_id = _create_payment_pending_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/payment/reconcile",
        json={
            "receipt_reference": "manual-0001",
            "amount": 5000,
            "currency": "AED",
            "reason": "bank transfer confirmed",
        },
        headers=auth_headers("finance_officer"),
    )
    assert response.status_code == 200
    assert response.json()["current_status"] == "paid"
