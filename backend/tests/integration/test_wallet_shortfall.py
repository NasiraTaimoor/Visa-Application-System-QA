"""Insufficient-balance submission is blocked without reservation (T088).
Traceability: TS-FR-013/TC-FR-013, BR-007, E-004, SC-005."""

from tests.conftest import auth_headers


def _create_ready_application_for_agency(client, agency_id):
    create = client.post(
        "/api/v1/applications",
        json={"visa_type": "tourist", "owning_sub_agency_id": agency_id, "consent_given": True},
        headers=auth_headers("applicant"),
    )
    application_id = create.json()["application_id"]
    client.patch(
        f"/api/v1/applications/{application_id}",
        json={
            "expected_version": 1,
            "applicant_fields": {
                "legal_name": "John Roe",
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


def test_insufficient_balance_blocks_submission_without_reservation(client):
    # sub-agency-002's mocked balance (500) is below the tourist-visa fee (5000).
    application_id = _create_ready_application_for_agency(client, "sub-agency-002")

    verify = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers={"Authorization": "Bearer u-subagency-2"},
    )
    assert verify.status_code == 200
    body = verify.json()
    assert body["sufficient"] is False
    assert body["reservation_reference"] is None
    assert body["shortfall_amount"] == 4500

    # The case remains ready_for_sub_agency_review (unchanged) and submission is blocked.
    submit = client.post(
        f"/api/v1/applications/{application_id}/submit",
        headers={"Authorization": "Bearer u-subagency-2"},
    )
    assert submit.status_code == 400
