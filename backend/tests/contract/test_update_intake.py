from tests.conftest import auth_headers


def _create_draft(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("applicant"),
    )
    return response.json()["application_id"]


def test_update_intake_returns_missing_items_and_bumps_version(client):
    application_id = _create_draft(client)
    response = client.patch(
        f"/api/v1/applications/{application_id}",
        json={"expected_version": 1, "applicant_fields": {"legal_name": "Jane Doe"}},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["current_version"] == 2
    assert "applicant.date_of_birth" in body["missing_items"]


def test_update_intake_rejects_stale_version(client):
    application_id = _create_draft(client)
    response = client.patch(
        f"/api/v1/applications/{application_id}",
        json={"expected_version": 99, "applicant_fields": {}},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 400
