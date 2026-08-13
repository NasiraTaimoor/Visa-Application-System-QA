from tests.conftest import auth_headers


def test_create_application_returns_draft_case_reference(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == "draft_created"
    assert body["case_reference"].startswith("VA-")
    assert "correlation_reference" in body


def test_create_application_without_consent_is_rejected(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": False,
        },
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 400
