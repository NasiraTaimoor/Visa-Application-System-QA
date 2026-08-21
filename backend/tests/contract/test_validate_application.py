from tests.conftest import auth_headers


def test_validate_application_reports_blocking_findings_when_incomplete(client):
    create = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("applicant"),
    )
    application_id = create.json()["application_id"]

    response = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_ready"] is False
    assert any(f["rule_id"] == "required_fields" for f in body["findings"])
