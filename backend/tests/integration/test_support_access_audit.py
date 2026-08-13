"""Support access event and business reason are recorded (T161).
Traceability: TS-FR-030/TC-FR-030, BR-035."""

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


def test_support_access_requires_reason_and_is_audited(client):
    application_id = _create_draft(client)

    denied = client.post(
        f"/api/v1/support/cases/{application_id}/access",
        json={"business_reason": ""},
        headers=auth_headers("support_admin"),
    )
    assert denied.status_code == 400

    accessed = client.post(
        f"/api/v1/support/cases/{application_id}/access",
        json={"business_reason": "applicant reported a stuck draft via support ticket #4821"},
        headers=auth_headers("support_admin"),
    )
    assert accessed.status_code == 200
    assert accessed.json()["current_status"] == "draft_created"

    audit = client.get(
        f"/api/v1/audit/events?application_id={application_id}",
        headers=auth_headers("auditor_compliance"),
    )
    support_events = [e for e in audit.json()["events"] if e["action"] == "support.access"]
    assert len(support_events) == 1
    assert (
        support_events[0]["reason"] == "applicant reported a stuck draft via support ticket #4821"
    )
