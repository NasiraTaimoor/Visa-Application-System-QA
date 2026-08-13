from tests.conftest import auth_headers


def test_calculate_fees_returns_amount_and_fee_version(client):
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

    response = client.get(
        f"/api/v1/applications/{application_id}/fees", headers=auth_headers("applicant")
    )
    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == 5000
    assert body["currency"] == "AED"
    assert body["fee_version"] == "2026.1"
