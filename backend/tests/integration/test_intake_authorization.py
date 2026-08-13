"""Denies unauthorized draft creation/resume (scope/consent prerequisites) (T039)."""

from tests.conftest import auth_headers


def test_role_without_intake_permission_is_denied(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("auditor_compliance"),
    )
    assert response.status_code == 403


def test_cross_agency_intake_write_is_denied(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-999",
            "consent_given": True,
        },
        headers=auth_headers("sub_agency_officer"),
    )
    assert response.status_code == 403


def test_missing_identity_token_is_denied(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
    )
    assert response.status_code == 401
