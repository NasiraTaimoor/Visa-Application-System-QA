"""Notification retry exhaustion recorded and visible to support without
blocking the case workflow (T145). Traceability: TS-FR-028/TC-FR-028, E-016."""

from tests.conftest import auth_headers


def test_notification_delivery_failure_is_recorded_but_does_not_block_workflow(client):
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
                "legal_name": "NOTIFY_FAIL Doe",
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
    validate = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    # The case workflow proceeds normally even though notifications for this
    # applicant will fail to deliver.
    assert validate.status_code == 200

    verify = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers=auth_headers("sub_agency_officer"),
    )
    assert verify.status_code == 200
    submit = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    assert submit.status_code == 200
    assert submit.json()["current_status"] == "submitted_to_main_agency"

    from src.config import get_policy_config
    from src.db.base import SessionLocal
    from src.notifications.models.notification import Notification

    with SessionLocal() as db:
        submission_notification = (
            db.query(Notification)
            .filter_by(
                application_id=application_id,
                event_type="submission_created",
                recipient_category="applicant",
            )
            .one()
        )
        assert submission_notification.delivery_status == "failed"
        assert submission_notification.retry_status == "exhausted"
        assert submission_notification.attempt_count == get_policy_config().notification_retry_limit
        assert submission_notification.failure_reason is not None
