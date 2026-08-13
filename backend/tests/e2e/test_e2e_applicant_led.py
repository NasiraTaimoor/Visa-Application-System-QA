"""End-to-end applicant-led full lifecycle smoke suite: draft through final
decision (T178). Traceability: TS-FR-001-042 (representative smoke path),
TC-FR-001-042; quickstart.md Core Validation Flow steps 1-12.
"""

from tests.conftest import auth_headers


def test_applicant_led_journey_from_draft_to_approved(client):
    create = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("applicant"),
    )
    assert create.status_code == 200
    application_id = create.json()["application_id"]
    assert create.json()["current_status"] == "draft_created"

    update = client.patch(
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
    assert update.status_code == 200

    resumed = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )
    assert resumed.status_code == 200
    assert resumed.json()["applicant"]["legal_name"] == "Jane Doe"

    upload_passport = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    assert upload_passport.status_code == 200
    document_id = upload_passport.json()["document_id"]

    ocr = client.get(f"/api/v1/documents/{document_id}/ocr", headers=auth_headers("applicant"))
    assert ocr.status_code == 200

    confirm_ocr = client.post(
        f"/api/v1/applications/{application_id}/documents/{document_id}/ocr/confirm",
        json={"reviewed_values": {"passport_number": "P1234567"}},
        headers=auth_headers("applicant"),
    )
    assert confirm_ocr.status_code == 200

    upload_photo = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "photo"},
        files={"file": ("photo.jpg", b"fake bytes", "image/jpeg")},
        headers=auth_headers("applicant"),
    )
    assert upload_photo.status_code == 200

    validate = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    assert validate.status_code == 200
    assert validate.json()["current_status"] == "ready_for_sub_agency_review"

    verify = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    assert verify.status_code == 200
    assert verify.json()["sufficient"] is True

    submit = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    assert submit.status_code == 200
    assert submit.json()["current_status"] == "submitted_to_main_agency"

    claim = client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert claim.json()["current_status"] == "main_agency_processing"

    readiness = client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": "documents verified"},
        headers=auth_headers("main_agency_case_officer"),
    )
    assert readiness.status_code == 200

    gdrfa = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert gdrfa.json()["response_type"] == "acknowledged"
    assert gdrfa.json()["current_status"] == "payment_pending"

    payment = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert payment.json()["payment_state"] == "paid"
    assert payment.json()["current_status"] == "paid"

    decision = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert decision.json()["current_status"] == "approved"

    outcome = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )
    assert outcome.json()["current_status"] == "approved"

    audit = client.get(
        f"/api/v1/audit/events?application_id={application_id}",
        headers=auth_headers("auditor_compliance"),
    )
    assert len(audit.json()["events"]) >= 10
