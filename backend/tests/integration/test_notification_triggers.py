"""Notification triggering on submission, correction, validation failure,
wallet shortfall, payment, GDRFA, immigration, and final-decision events
(T144). Traceability: TS-FR-025-026/TC-FR-025-026."""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def _notification_event_types(application_id):
    from src.db.base import SessionLocal
    from src.notifications.models.notification import Notification

    with SessionLocal() as db:
        return {
            n.event_type
            for n in db.query(Notification).filter_by(application_id=application_id).all()
        }


def test_wallet_shortfall_triggers_notification(client):
    create = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-002",
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
    client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers={"Authorization": "Bearer u-subagency-2"},
    )

    assert "wallet_shortfall" in _notification_event_types(application_id)


def test_full_lifecycle_triggers_expected_notification_events(client):
    application_id = _create_payment_pending_application(client)
    events_after_submission = _notification_event_types(application_id)
    assert "submission_created" in events_after_submission
    assert "gdrfa_response" in events_after_submission

    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )

    final_events = _notification_event_types(application_id)
    assert "payment_outcome" in final_events
    assert "final_decision" in final_events
