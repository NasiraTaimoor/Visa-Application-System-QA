"""Rejected uploads (type/size/quality/corruption/security) keep the case
editable (T064). Traceability: TS-FR-005/TC-FR-005, E-001."""

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


def test_unsupported_file_type_is_rejected_and_case_stays_editable(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.exe", b"not a real document", "application/octet-stream")},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    assert response.json()["screening_status"] == "rejected"

    # The case remains editable: a valid replacement upload is still accepted.
    retry = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    assert retry.status_code == 200
    assert retry.json()["screening_status"] == "accepted"


def test_security_screening_failure_is_rejected(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 MALWARE_TEST_MARKER bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    assert response.json()["screening_status"] == "rejected"


def test_corrupted_document_is_rejected(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"CORRUPT_TEST_MARKER", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 200
    assert response.json()["screening_status"] == "rejected"
