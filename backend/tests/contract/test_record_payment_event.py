from tests.conftest import auth_headers


def _create_payment_pending_application(client, legal_name="Jane Doe"):
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
                "legal_name": legal_name,
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
    client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": "verified"},
        headers=auth_headers("main_agency_case_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    return application_id


def test_confirm_payment_marks_paid_and_debits_wallet(client):
    application_id = _create_payment_pending_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["payment_state"] == "paid"
    assert body["current_status"] == "paid"

    from src.db.base import SessionLocal
    from src.finance.models.wallet_ledger_event import WalletLedgerEvent

    with SessionLocal() as db:
        debit = (
            db.query(WalletLedgerEvent)
            .filter_by(application_id=application_id, event_type="debit")
            .one_or_none()
        )
        assert debit is not None


def test_confirm_payment_failure_moves_to_payment_failed(client):
    application_id = _create_payment_pending_application(client, legal_name="PAYMENT_FAIL Doe")
    response = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["payment_state"] == "failed"
    assert body["current_status"] == "payment_failed"
