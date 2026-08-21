from tests.conftest import auth_headers


def _create_and_upload_passport(client, content=b"%PDF-1.4 bytes"):
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
    upload = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", content, "application/pdf")},
        headers=auth_headers("applicant"),
    )
    return application_id, upload.json()["document_id"]


def test_confirm_ocr_values_records_reviewer_and_values(client):
    application_id, document_id = _create_and_upload_passport(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/documents/{document_id}/ocr/confirm",
        json={"reviewed_values": {"passport_number": "P1234567"}, "correction_reason": None},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reviewer_id"] == "u-applicant-1"
    assert body["reviewed_values"]["passport_number"] == "P1234567"


def test_confirm_ocr_values_below_blocking_threshold_requires_corrected_values(client):
    application_id, document_id = _create_and_upload_passport(
        client, content=b"%PDF-1.4 OCR_LOW_CONFIDENCE bytes"
    )
    response = client.post(
        f"/api/v1/applications/{application_id}/documents/{document_id}/ocr/confirm",
        json={"reviewed_values": {}},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 400
