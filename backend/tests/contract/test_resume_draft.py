from tests.conftest import auth_headers


def test_resume_draft_masks_date_of_birth_for_non_privileged_role(client):
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
    client.patch(
        f"/api/v1/applications/{application_id}",
        json={
            "expected_version": 1,
            "applicant_fields": {"legal_name": "Jane Doe", "date_of_birth": "1990-05-14"},
        },
        headers=auth_headers("applicant"),
    )

    response = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )
    assert response.status_code == 200
    body = response.json()
    assert body["applicant"]["date_of_birth"] != "1990-05-14"
    assert body["applicant"]["date_of_birth"].endswith("14")
