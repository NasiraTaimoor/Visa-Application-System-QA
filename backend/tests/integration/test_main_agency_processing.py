"""Routing, assignment, correction request, and readiness approval (T104).
Traceability: TS-FR-017-019, TC-FR-017-019."""

from tests.conftest import auth_headers


def _create_submitted_application(client, legal_name="Jane Doe"):
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
            "applicant_fields": {
                "legal_name": legal_name,
                "date_of_birth": "1990-05-14",
                "nationality": "GBR",
            },
            "passport_fields": {
                "passport_number": "P1234567",
                "issuing_country": "GBR",
                "issue_date": "2020-01-01",
                "expiry_date": "2030-05-13",
            },
        },
        headers=auth_headers("applicant"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "photo"},
        files={"file": ("photo.jpg", b"fake bytes", "image/jpeg")},
        headers=auth_headers("applicant"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    return application_id


def test_routed_case_claim_correction_and_readiness_flow(client):
    application_id = _create_submitted_application(client)

    claim = client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert claim.json()["current_status"] == "main_agency_processing"

    correction = client.post(
        f"/api/v1/applications/{application_id}/correction-request",
        json={"reason": "sponsor letter is missing a signature", "responsible_party": "applicant"},
        headers=auth_headers("main_agency_case_officer"),
    )
    assert correction.json()["current_status"] == "correction_requested"

    resolved = client.post(
        f"/api/v1/applications/{application_id}/correction-resolve",
        headers=auth_headers("applicant"),
    )
    assert resolved.json()["current_status"] == "main_agency_processing"

    readiness = client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": "all documents verified"},
        headers=auth_headers("main_agency_case_officer"),
    )
    assert readiness.status_code == 200


def test_readiness_without_reason_is_rejected(client):
    application_id = _create_submitted_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )

    response = client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": ""},
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 400
