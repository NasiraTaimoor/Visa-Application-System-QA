from tests.conftest import auth_headers
from tests.contract.test_wallet_events import _create_ready_application


def test_submit_to_main_agency_returns_submission_reference(client):
    application_id = _create_ready_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )

    response = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    assert response.status_code == 200
    body = response.json()
    assert body["submission_reference"].startswith("SUB-")
    assert body["current_status"] == "submitted_to_main_agency"


def test_submit_without_wallet_verification_is_rejected(client):
    application_id = _create_ready_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    assert response.status_code == 400
