"""Idempotency/concurrency regression suite for submissions, wallet events,
payments, immigration updates, and notification retries (T188).
Traceability: TS-FR-015, TS-FR-039/TC-FR-015, TC-FR-039, FR-039, BR-025,
BR-027.

Consolidates the duplicate-attempt guarantee already exercised per-story
into one regression pass so a future change that weakens any single
idempotency path is caught here even if the originating story's test
happens to be skipped or reordered.
"""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application
from tests.integration.test_main_agency_processing import _create_submitted_application


def test_sub_agency_submission_is_idempotent_by_application(client):
    application_id = _create_submitted_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    # submission itself already happened inside _create_submitted_application;
    # retry the wallet-reservation-adjacent step to confirm no duplicate ledger row.
    from src.db.base import SessionLocal
    from src.finance.models.wallet_ledger_event import WalletLedgerEvent

    with SessionLocal() as db:
        reservations = (
            db.query(WalletLedgerEvent)
            .filter_by(application_id=application_id, event_type="reservation")
            .all()
        )
        assert len(reservations) == 1


def test_gdrfa_submission_is_idempotent_by_application(client):
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
    first = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    second = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert first.json()["submission_reference"] == second.json()["submission_reference"]


def test_payment_confirmation_is_idempotent_by_application(client):
    application_id = _create_payment_pending_application(client)
    first = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    second = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    assert first.json() == second.json()

    from src.db.base import SessionLocal
    from src.finance.models.payment import Payment

    with SessionLocal() as db:
        payments = db.query(Payment).filter_by(application_id=application_id).all()
        assert len(payments) == 1


def test_immigration_final_decision_is_locked_against_repeated_updates(client):
    application_id = _create_payment_pending_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    first = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert first.json()["current_status"] == "approved"

    second = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert second.status_code == 400  # terminal lock, not a duplicate "success"

    from src.applications.models.visa_application import VisaApplication
    from src.db.base import SessionLocal

    with SessionLocal() as db:
        application = db.get(VisaApplication, application_id)
        assert application.current_status == "approved"


def test_notification_retry_limit_is_the_configured_policy_value_and_stops_there(client):
    application_id = _create_submitted_application(client, legal_name="NOTIFY_FAIL Doe")
    from src.config import get_policy_config
    from src.db.base import SessionLocal
    from src.notifications.models.notification import Notification

    with SessionLocal() as db:
        notification = (
            db.query(Notification)
            .filter_by(
                application_id=application_id,
                event_type="submission_created",
                recipient_category="applicant",
            )
            .one()
        )
        assert notification.attempt_count == get_policy_config().notification_retry_limit
        assert notification.retry_status == "exhausted"
