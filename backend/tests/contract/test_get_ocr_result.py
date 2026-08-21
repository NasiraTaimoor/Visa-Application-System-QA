from tests.conftest import auth_headers


def test_get_ocr_result_returns_extracted_fields_and_confidence(client):
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
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    document_id = upload.json()["document_id"]

    response = client.get(f"/api/v1/documents/{document_id}/ocr", headers=auth_headers("applicant"))
    assert response.status_code == 200
    body = response.json()
    assert body["extraction_status"] == "completed"
    assert body["overall_confidence"] == 0.93
    assert body["extracted_fields"]["passport_number"] == "P1234567"
