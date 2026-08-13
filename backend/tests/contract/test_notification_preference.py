"""Contract test for Create notification preference API (T142).
Traceability: TS-FR-027/TC-FR-027, FR-027."""

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


def test_create_notification_preference_stores_channel_and_opt_outs(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/notification-preferences",
        json={"channel": "sms", "opted_out_events": ["submission_created"]},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["channel"] == "sms"
    assert body["opted_out_events"] == ["submission_created"]


def test_mandatory_events_cannot_be_opted_out(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/notification-preferences",
        json={
            "channel": "sms",
            "opted_out_events": ["correction_requested", "final_decision", "submission_created"],
        },
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["opted_out_events"] == ["submission_created"]
