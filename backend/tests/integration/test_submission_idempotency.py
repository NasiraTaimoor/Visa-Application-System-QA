"""Concurrent/duplicate submission attempts produce one reservation and one
submission (T089). Traceability: TS-FR-015/TC-FR-015, BR-025, BR-027,
E-005, SC-004."""

from tests.conftest import auth_headers


def _create_ready_application(client):
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
    return application_id


def test_duplicate_wallet_verify_attempts_create_one_reservation(client):
    application_id = _create_ready_application(client)

    first = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    # A retry after the reservation already exists is rejected by the status
    # precondition (case is now wallet_verified, not ready_for_sub_agency_review),
    # which is itself the duplicate-prevention mechanism required by BR-025.
    second = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    assert first.status_code == 200
    assert second.status_code == 400

    from src.db.base import SessionLocal
    from src.finance.models.wallet_ledger_event import WalletLedgerEvent

    with SessionLocal() as db:
        reservations = (
            db.query(WalletLedgerEvent)
            .filter_by(application_id=application_id, event_type="reservation", status="active")
            .all()
        )
        assert len(reservations) == 1


def test_duplicate_submit_returns_same_submission_reference(client):
    application_id = _create_ready_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )

    first = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    second = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["submission_reference"] == second.json()["submission_reference"]

    from src.applications.models.submission import Submission
    from src.db.base import SessionLocal

    with SessionLocal() as db:
        submissions = db.query(Submission).filter_by(application_id=application_id).all()
        assert len(submissions) == 1
