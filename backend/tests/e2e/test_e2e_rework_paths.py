"""End-to-end rework-path suite: validation failure, correction, GDRFA
rejection, payment failure, immigration action-required (T180).
Traceability: TS-FR-009-011, TS-FR-018, TS-FR-021, TS-FR-023-024,
TC-FR-009-011, TC-FR-018, TC-FR-021, TC-FR-023-024; quickstart.md End-to-End
Testing rework path.
"""

from tests.conftest import auth_headers


def test_validation_failure_then_correction_via_main_agency(client):
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

    # Deliberately incomplete: only passport uploaded, no photo, no intake fields.
    client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    first_validation = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    assert first_validation.json()["is_ready"] is False
    assert first_validation.json()["current_status"] != "ready_for_sub_agency_review"

    # Applicant corrects: fills required fields and uploads the missing document.
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
        data={"document_type": "photo"},
        files={"file": ("photo.jpg", b"fake bytes", "image/jpeg")},
        headers=auth_headers("applicant"),
    )
    second_validation = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    assert second_validation.json()["is_ready"] is True
    assert second_validation.json()["current_status"] == "ready_for_sub_agency_review"


def test_gdrfa_rejection_returns_to_correction_requested(client):
    from tests.integration.test_gdrfa_outcomes import _claim_and_approve
    from tests.integration.test_main_agency_processing import _create_submitted_application

    application_id = _create_submitted_application(client, legal_name="GDRFA_REJECT Doe")
    _claim_and_approve(client, application_id)

    rejection = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert rejection.json()["current_status"] == "correction_requested"

    resolved = client.post(
        f"/api/v1/applications/{application_id}/correction-resolve",
        headers=auth_headers("applicant"),
    )
    assert resolved.json()["current_status"] == "main_agency_processing"


def test_payment_failure_then_finance_reconciliation_recovers_the_case(client):
    from tests.contract.test_record_payment_event import _create_payment_pending_application

    application_id = _create_payment_pending_application(client, legal_name="PAYMENT_FAIL Doe")
    failure = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert failure.json()["current_status"] == "payment_failed"

    reconciled = client.post(
        f"/api/v1/applications/{application_id}/payment/reconcile",
        json={
            "receipt_reference": "manual-recovery",
            "amount": 5000,
            "currency": "AED",
            "reason": "confirmed via bank statement",
        },
        headers=auth_headers("finance_officer"),
    )
    assert reconciled.json()["current_status"] == "paid"


def test_immigration_action_required_then_final_decision(client):
    from tests.contract.test_record_payment_event import _create_payment_pending_application

    application_id = _create_payment_pending_application(
        client, legal_name="IMM_ACTION_REQUIRED Doe"
    )
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )

    action_required = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert action_required.json()["response_type"] == "action_required"
    assert action_required.json()["current_status"] == "immigration_processing"

    client.patch(
        f"/api/v1/applications/{application_id}",
        json={"expected_version": 2, "applicant_fields": {"legal_name": "Jane Doe"}},
        headers=auth_headers("applicant"),
    )
    final = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert final.json()["current_status"] == "approved"
