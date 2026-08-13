from tests.conftest import auth_headers


def _create_draft(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("applicant"),
    )
    return response.json()["application_id"]


def test_upload_document_accepts_valid_file_and_triggers_ocr_for_passport(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 fake passport bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["screening_status"] == "accepted"
    assert body["version"] == 1
    assert body["ocr_triggered"] is True


def test_upload_document_rejects_oversized_file(client):
    application_id = _create_draft(client)
    from src.config import get_policy_config

    oversized = b"0" * (get_policy_config().document_max_size_bytes + 1)
    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "photo"},
        files={"file": ("photo.jpg", oversized, "image/jpeg")},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    assert response.json()["screening_status"] == "rejected"
