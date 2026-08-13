from tests.conftest import auth_headers


def test_get_audit_history_returns_events_for_case(client):
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
        f"/api/v1/audit/events?application_id={application_id}",
        headers=auth_headers("auditor_compliance"),
    )
    assert response.status_code == 200
    events = response.json()["events"]
    assert len(events) >= 1
    assert events[0]["action"] == "application.create"


def test_get_audit_history_denies_non_auditor(client):
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
        f"/api/v1/audit/events?application_id={application_id}", headers=auth_headers("applicant")
    )
    assert response.status_code == 403
