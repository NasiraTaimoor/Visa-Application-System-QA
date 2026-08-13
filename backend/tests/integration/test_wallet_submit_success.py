"""Sufficient-balance submission creates exactly one reservation and one
submission reference (T087). Traceability: TS-FR-012-014, TS-FR-016,
TS-FR-038, TC-FR-012-014, TC-FR-016, TC-FR-038; AC-003, SC-004."""

from tests.conftest import auth_headers


def _create_ready_application(client):
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
    return application_id


def test_sufficient_balance_creates_single_reservation_and_submission(client):
    application_id = _create_ready_application(client)

    verify = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    assert verify.json()["sufficient"] is True

    submit = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    assert submit.status_code == 200
    body = submit.json()
    assert body["current_status"] == "submitted_to_main_agency"
    assert body["snapshot_id"].startswith("snapshot-")

    # A second wallet verify attempt on the now-submitted case must not create
    # a second reservation: the status precondition alone blocks it.
    second_verify = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    assert second_verify.status_code == 400
