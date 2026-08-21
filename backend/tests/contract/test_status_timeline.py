from tests.conftest import auth_headers


def test_status_timeline_returns_chronological_events(client):
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
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )

    response = client.get(
        f"/api/v1/applications/{application_id}/status-timeline", headers=auth_headers("applicant")
    )
    assert response.status_code == 200
    timeline = response.json()["timeline"]
    assert len(timeline) == 1
    assert timeline[0]["new_status"] == "documents_pending"


def test_status_timeline_denies_unauthorized_role(client):
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
        f"/api/v1/applications/{application_id}/status-timeline",
        headers=auth_headers("system_service"),
    )
    assert response.status_code == 403
