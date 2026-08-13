"""OCR mismatch blocks submission until correction or authorized override
(T065). Traceability: TS-FR-006/TC-FR-006, BR-018, E-013."""

from tests.conftest import auth_headers


def _create_application_with_mismatched_passport(client):
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
                "passport_number": "P0000000",  # differs from the mocked OCR extraction
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
    client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "photo"},
        files={"file": ("photo.jpg", b"fake bytes", "image/jpeg")},
        headers=auth_headers("applicant"),
    )
    return application_id, upload.json()["document_id"]


def test_unconfirmed_ocr_mismatch_blocks_readiness(client):
    application_id, _document_id = _create_application_with_mismatched_passport(client)

    validate = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    body = validate.json()
    assert body["is_ready"] is False
    mismatch = next(f for f in body["findings"] if f["rule_id"] == "ocr_mismatch")
    assert mismatch["severity"] == "overrideable_blocking"
    assert body["current_status"] == "ocr_and_validation"


def test_supervisor_override_unblocks_readiness(client):
    application_id, _document_id = _create_application_with_mismatched_passport(client)
    validate = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    finding_id = next(f for f in validate.json()["findings"] if f["rule_id"] == "ocr_mismatch")[
        "finding_id"
    ]

    override = client.post(
        f"/api/v1/validation/findings/{finding_id}/override",
        json={"reason": "Applicant confirmed passport number by phone"},
        headers=auth_headers("main_agency_case_officer"),  # not a supervisor: must be denied
    )
    assert override.status_code == 403

    override = client.post(
        f"/api/v1/validation/findings/{finding_id}/override",
        json={"reason": "Applicant confirmed passport number by phone"},
        headers=auth_headers("main_agency_supervisor"),
    )
    assert override.status_code == 200
    assert override.json()["override_status"] == "approved"
