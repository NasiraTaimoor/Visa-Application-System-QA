"""Performance test validating SC-002, SC-006, SC-010 timing thresholds:
2-minute OCR/upload status, 5-minute integration visibility, 1-minute
notification queueing (T182).

Honesty note: the mocked adapters (OCR, GDRFA, immigration, notification
gateway) all respond synchronously and immediately in this scaffold, so
these assertions demonstrate the code path itself adds negligible latency
relative to the SLA budgets — they do not measure a real OCR vendor's
processing time or a real network round trip, which can only be validated
against the actual integrated services in a deployed environment.
"""

import time

from tests.conftest import auth_headers

SC_002_UPLOAD_OCR_SECONDS = 120
SC_006_INTEGRATION_VISIBILITY_SECONDS = 300
SC_010_NOTIFICATION_QUEUEING_SECONDS = 60


def test_upload_and_ocr_status_available_within_sc_002_budget(client):
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

    start = time.perf_counter()
    upload = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    document_id = upload.json()["document_id"]
    ocr = client.get(f"/api/v1/documents/{document_id}/ocr", headers=auth_headers("applicant"))
    elapsed = time.perf_counter() - start

    assert upload.json()["screening_status"] == "accepted"
    assert ocr.json()["extraction_status"] == "completed"
    assert elapsed < SC_002_UPLOAD_OCR_SECONDS


def test_gdrfa_response_visible_within_sc_006_budget(client):
    from tests.integration.test_main_agency_processing import _create_submitted_application

    application_id = _create_submitted_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": "verified"},
        headers=auth_headers("main_agency_case_officer"),
    )

    start = time.perf_counter()
    gdrfa = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    elapsed = time.perf_counter() - start

    assert gdrfa.json()["response_type"] == "acknowledged"
    assert elapsed < SC_006_INTEGRATION_VISIBILITY_SECONDS


def test_notification_queued_within_sc_010_budget(client):
    from tests.integration.test_main_agency_processing import _create_submitted_application

    start = time.perf_counter()
    application_id = _create_submitted_application(client)
    elapsed = time.perf_counter() - start

    from src.db.base import SessionLocal
    from src.notifications.models.notification import Notification

    with SessionLocal() as db:
        notification = (
            db.query(Notification)
            .filter_by(application_id=application_id, event_type="submission_created")
            .first()
        )
        assert notification is not None
        assert notification.delivery_status in (
            "delivered",
            "failed",
        )  # queued and attempted, either outcome
    assert elapsed < SC_010_NOTIFICATION_QUEUEING_SECONDS
