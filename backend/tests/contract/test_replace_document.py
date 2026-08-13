from tests.conftest import auth_headers


def _create_draft_with_passport(client):
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
        files={"file": ("passport.pdf", b"%PDF-1.4 original bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    return application_id, upload.json()["document_id"]


def test_replace_document_creates_new_version_and_invalidates_ocr(client):
    application_id, document_id = _create_draft_with_passport(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/documents/{document_id}/replace",
        files={"file": ("passport-v2.pdf", b"%PDF-1.4 corrected bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == 2
    assert body["document_id"] != document_id
    assert body["ocr_triggered"] is True
