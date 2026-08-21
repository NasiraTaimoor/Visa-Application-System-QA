"""Denies unauthorized audit/export access (T162). Traceability:
TS-FR-032-034/TC-FR-032-034, BR-006, E-009."""

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


def test_applicant_cannot_read_audit_history(client):
    application_id = _create_draft(client)
    response = client.get(
        f"/api/v1/audit/events?application_id={application_id}", headers=auth_headers("applicant")
    )
    assert response.status_code == 403


def test_sub_agency_officer_cannot_export(client):
    response = client.post(
        "/api/v1/audit/export",
        json={"business_reason": "attempting export"},
        headers=auth_headers("sub_agency_officer"),
    )
    assert response.status_code == 403


def test_finance_officer_cannot_resolve_recovery_tasks(client):
    response = client.post(
        "/api/v1/recovery/tasks/nonexistent/resolve",
        json={"business_reason": "test"},
        headers=auth_headers("finance_officer"),
    )
    assert response.status_code == 403


def test_main_agency_officer_cannot_access_support_case_lookup(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/support/cases/{application_id}/access",
        json={"business_reason": "test"},
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 403


def test_unauthenticated_request_is_denied(client):
    response = client.get("/api/v1/audit/events")
    assert response.status_code == 401
