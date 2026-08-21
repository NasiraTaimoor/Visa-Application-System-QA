from tests.conftest import auth_headers


def test_abandon_draft_transitions_to_abandoned(client):
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
        f"/api/v1/applications/{application_id}/abandon",
        json={"reason": "applicant no longer needs this visa"},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    assert response.json()["current_status"] == "abandoned"


def test_abandon_draft_is_not_allowed_twice(client):
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
    client.post(
        f"/api/v1/applications/{application_id}/abandon",
        json={"reason": "first abandon"},
        headers=auth_headers("applicant"),
    )
    response = client.post(
        f"/api/v1/applications/{application_id}/abandon",
        json={"reason": "second abandon"},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 409
