from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def _create_paid_application(client, legal_name="Jane Doe"):
    application_id = _create_payment_pending_application(client, legal_name=legal_name)
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    return application_id


def test_record_immigration_update_transitions_to_approved(client):
    application_id = _create_paid_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == "approved"
    assert body["quarantined"] is False
