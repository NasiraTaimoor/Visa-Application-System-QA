from tests.conftest import auth_headers


def _create_ready_application(client, owning_sub_agency_id="sub-agency-001"):
    create = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": owning_sub_agency_id,
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
    validate = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    assert validate.json()["current_status"] == "ready_for_sub_agency_review"
    return application_id


def test_verify_wallet_records_reservation_for_sufficient_balance(client):
    application_id = _create_ready_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sufficient"] is True
    assert body["reservation_reference"] is not None


def test_verify_wallet_denies_cross_agency_officer(client):
    application_id = _create_ready_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers={"Authorization": "Bearer u-subagency-2"},
    )
    assert response.status_code == 403
