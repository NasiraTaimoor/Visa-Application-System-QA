from tests.conftest import auth_headers


def test_export_requires_business_reason(client):
    response = client.post(
        "/api/v1/audit/export",
        json={"business_reason": ""},
        headers=auth_headers("auditor_compliance"),
    )
    assert response.status_code == 400


def test_export_records_returns_reference_and_count(client):
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
        "/api/v1/audit/export",
        json={"application_id": application_id, "business_reason": "quarterly compliance review"},
        headers=auth_headers("auditor_compliance"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["export_reference"].startswith("EXPORT-")
    assert body["record_count"] >= 1
