"""Denies cross-agency case processing (T106). Traceability: BR-006, E-009."""

from tests.conftest import auth_headers
from tests.integration.test_main_agency_processing import _create_submitted_application


def test_officer_outside_routed_agency_cannot_claim(client):
    application_id = _create_submitted_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers={"Authorization": "Bearer u-mainagency-2"},
    )
    assert response.status_code == 403


def test_non_main_agency_role_cannot_claim(client):
    application_id = _create_submitted_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("finance_officer"),
    )
    assert response.status_code == 403


def test_officer_outside_routed_agency_cannot_request_correction(client):
    application_id = _create_submitted_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )

    response = client.post(
        f"/api/v1/applications/{application_id}/correction-request",
        json={"reason": "test", "responsible_party": "applicant"},
        headers={"Authorization": "Bearer u-mainagency-2"},
    )
    assert response.status_code == 403
