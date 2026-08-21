"""Upload -> screen -> OCR -> review -> correct -> validate flow (T063).

Traceability: TS-FR-005-TS-FR-011, TS-FR-037, TS-FR-042; TC-FR-005-TC-FR-011,
TC-FR-037, TC-FR-042 (User Story 2).
"""

from tests.conftest import auth_headers


def test_upload_screen_ocr_review_correct_validate_journey(client):
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
                "passport_number": "P9999999",
                "issuing_country": "GBR",
                "issue_date": "2020-01-01",
                "expiry_date": "2030-05-13",
            },
        },
        headers=auth_headers("applicant"),
    )

    upload = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    assert upload.status_code == 200
    document_id = upload.json()["document_id"]

    ocr = client.get(f"/api/v1/documents/{document_id}/ocr", headers=auth_headers("applicant"))
    assert ocr.status_code == 200
    assert (
        ocr.json()["extracted_fields"]["passport_number"] == "P1234567"
    )  # differs from entered value

    # Correct the mismatch by confirming the applicant-entered value as reviewed.
    confirm = client.post(
        f"/api/v1/applications/{application_id}/documents/{document_id}/ocr/confirm",
        json={
            "reviewed_values": {"passport_number": "P9999999"},
            "correction_reason": "matched applicant entry",
        },
        headers=auth_headers("applicant"),
    )
    assert confirm.status_code == 200

    for document_type in ("photo",):
        client.post(
            f"/api/v1/applications/{application_id}/documents",
            data={"document_type": document_type},
            files={"file": (f"{document_type}.jpg", b"fake bytes", "image/jpeg")},
            headers=auth_headers("applicant"),
        )

    validate = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    assert validate.status_code == 200
    body = validate.json()
    assert body["is_ready"] is True
    assert body["current_status"] == "ready_for_sub_agency_review"
