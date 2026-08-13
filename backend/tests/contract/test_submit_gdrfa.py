from tests.conftest import auth_headers
from tests.contract.test_process_main_agency_action import _create_submitted_application


def _claim_and_approve(client, application_id):
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": "all documents verified"},
        headers=auth_headers("main_agency_case_officer"),
    )


def test_submit_to_gdrfa_requires_readiness_approval(client):
    application_id = _create_submitted_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )

    response = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 400


def test_submit_to_gdrfa_acknowledged_moves_to_payment_pending(client):
    application_id = _create_submitted_application(client)
    _claim_and_approve(client, application_id)

    response = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["response_type"] == "acknowledged"
    assert body["current_status"] == "payment_pending"
