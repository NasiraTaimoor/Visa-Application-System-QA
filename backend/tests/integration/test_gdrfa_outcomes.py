"""GDRFA acknowledgement, rejection, action-required, timeout, and duplicate
outcomes (T105). Traceability: TS-FR-020-021, TC-FR-020-021, E-006, E-017."""

from tests.conftest import auth_headers
from tests.integration.test_main_agency_processing import _create_submitted_application


def _claim_and_approve(client, application_id):
    client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers=auth_headers("main_agency_case_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/readiness-approve",
        json={"reason": "verified"},
        headers=auth_headers("main_agency_case_officer"),
    )


def test_acknowledged_response_moves_to_payment_pending(client):
    application_id = _create_submitted_application(client, legal_name="Jane Doe")
    _claim_and_approve(client, application_id)

    response = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    body = response.json()
    assert body["response_type"] == "acknowledged"
    assert body["current_status"] == "payment_pending"


def test_rejected_response_returns_to_correction_requested(client):
    application_id = _create_submitted_application(client, legal_name="GDRFA_REJECT Doe")
    _claim_and_approve(client, application_id)

    response = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    body = response.json()
    assert body["response_type"] == "rejected"
    assert body["current_status"] == "correction_requested"
    assert body["response_reason"] == "missing_supporting_document"


def test_timeout_response_keeps_case_pending_and_creates_recovery_task(client):
    application_id = _create_submitted_application(client, legal_name="GDRFA_TIMEOUT Doe")
    _claim_and_approve(client, application_id)

    response = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    body = response.json()
    assert body["response_type"] == "timeout"
    assert body["current_status"] == "gdrfa_submitted"

    from src.agencies.models.processing_task import ProcessingTask
    from src.db.base import SessionLocal

    with SessionLocal() as db:
        tasks = db.query(ProcessingTask).filter_by(application_id=application_id).all()
        assert any(t.task_type == "gdrfa_timeout" for t in tasks)


def test_action_required_response_keeps_case_pending(client):
    application_id = _create_submitted_application(client, legal_name="GDRFA_ACTION_REQUIRED Doe")
    _claim_and_approve(client, application_id)

    response = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    body = response.json()
    assert body["response_type"] == "action_required"
    assert body["current_status"] == "gdrfa_submitted"


def test_duplicate_submit_attempt_returns_same_outcome(client):
    application_id = _create_submitted_application(client, legal_name="Jane Doe")
    _claim_and_approve(client, application_id)

    first = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    second = client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )
    assert first.json()["submission_reference"] == second.json()["submission_reference"]

    from src.applications.models.submission import Submission
    from src.db.base import SessionLocal

    with SessionLocal() as db:
        submissions = (
            db.query(Submission)
            .filter_by(application_id=application_id, submission_type="gdrfa")
            .all()
        )
        assert len(submissions) == 1
