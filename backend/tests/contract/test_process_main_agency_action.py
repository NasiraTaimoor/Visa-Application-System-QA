from tests.conftest import auth_headers


def _create_submitted_application(client):
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
                "legal_name": "Jane Doe",
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


def test_claim_transitions_to_main_agency_processing(client):
    application_id = _create_submitted_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 200
    assert response.json()["current_status"] == "main_agency_processing"


def test_correction_request_requires_reason(client):
    application_id = _create_submitted_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )

    response = client.post(
        f"/api/v1/applications/{application_id}/correction-request",
        json={"reason": "", "responsible_party": "applicant"},
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 400

    response = client.post(
        f"/api/v1/applications/{application_id}/correction-request",
        json={"reason": "passport photo is blurry", "responsible_party": "applicant"},
        headers=auth_headers("main_agency_case_officer"),
    )
    assert response.status_code == 200
    assert response.json()["current_status"] == "correction_requested"
