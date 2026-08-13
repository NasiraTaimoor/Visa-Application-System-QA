"""End-to-end sub-agency-led full lifecycle smoke suite (T179).
Traceability: TS-FR-001-042 (representative smoke path, sub-agency-created
case), TC-FR-001-042; quickstart.md Core Validation Flow steps 1-12.
"""

from tests.conftest import auth_headers


def test_sub_agency_led_journey_from_draft_to_approved(client):
    create = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "student",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
            "legal_name": "Ali Khan",
        },
        headers=auth_headers("sub_agency_officer"),
    )
    assert create.status_code == 200
    application_id = create.json()["application_id"]

    client.patch(
        f"/api/v1/applications/{application_id}",
        json={
            "expected_version": 1,
            "applicant_fields": {
                "legal_name": "Ali Khan",
                "date_of_birth": "1998-02-20",
                "nationality": "PAK",
            },
            "passport_fields": {
                # Matches the mocked OCR provider's default extraction so no
                # explicit OCR-confirmation step is needed in this smoke path.
                "passport_number": "P1234567",
                "issuing_country": "PAK",
                "issue_date": "2021-03-01",
                "expiry_date": "2031-03-01",
            },
        },
        headers=auth_headers("sub_agency_officer"),
    )

    passport_document_id = None
    for document_type, filename, content_type in (
        ("passport_bio_page", "passport.pdf", "application/pdf"),
        ("photo", "photo.jpg", "image/jpeg"),
        ("enrollment_letter", "enrollment.pdf", "application/pdf"),
    ):
        upload = client.post(
            f"/api/v1/applications/{application_id}/documents",
            data={"document_type": document_type},
            files={"file": (filename, b"fake bytes", content_type)},
            headers=auth_headers("sub_agency_officer"),
        )
        assert upload.status_code == 200
        if document_type == "passport_bio_page":
            passport_document_id = upload.json()["document_id"]

    # The mocked OCR provider always extracts the same default passport
    # data regardless of applicant identity; confirm the sub-agency-entered
    # values so validation does not flag them as unconfirmed mismatches.
    confirm = client.post(
        f"/api/v1/applications/{application_id}/documents/{passport_document_id}/ocr/confirm",
        json={"reviewed_values": {"date_of_birth": "1998-02-20", "nationality": "PAK"}},
        headers=auth_headers("sub_agency_officer"),
    )
    assert confirm.status_code == 200

    validate = client.post(
        f"/api/v1/applications/{application_id}/validate",
        headers=auth_headers("sub_agency_officer"),
    )
    assert validate.json()["current_status"] == "ready_for_sub_agency_review"

    verify = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    assert verify.json()["sufficient"] is True

    submit = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    assert submit.json()["current_status"] == "submitted_to_main_agency"

    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": "verified"},
        headers=auth_headers("main_agency_case_officer"),
    )
    gdrfa = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert gdrfa.json()["current_status"] == "payment_pending"

    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    decision = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert decision.json()["current_status"] == "approved"
