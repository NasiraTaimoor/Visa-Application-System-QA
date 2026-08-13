"""Payment pending-to-paid via authorized confirmation (T124). Traceability:
TS-FR-022/TC-FR-022, BR-023."""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_authorized_confirmation_moves_payment_pending_to_paid(client):
    application_id = _create_payment_pending_application(client)

    response = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert response.status_code == 200
    assert response.json()["current_status"] == "paid"

    # Immigration processing may now begin.
    next_step = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert next_step.status_code == 200
