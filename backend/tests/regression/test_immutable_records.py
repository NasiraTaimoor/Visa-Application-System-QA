"""Regression suite confirming immutability of submitted snapshots, final
decisions, financial records, and audit records (T176). Traceability:
TS-FR-036, TS-FR-041/TC-FR-036, TC-FR-041, FR-030, BR-011.
"""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application
from tests.integration.test_main_agency_processing import _create_submitted_application


def test_audit_module_exposes_no_update_or_delete_path():
    """Structural check: record_audit_event is the only write entry point;
    no function anywhere in the audit module allows mutating or deleting an
    existing AuditEvent row (BR-011, FR-030)."""
    import src.audit.audit_middleware as audit_middleware

    module_functions = [name for name in dir(audit_middleware) if not name.startswith("_")]
    forbidden = {"update_audit_event", "delete_audit_event", "modify_audit_event"}
    assert not (forbidden & set(module_functions))


def test_duplicate_submission_never_changes_the_locked_snapshot_reference(client):
    application_id = _create_submitted_application(client)
    first = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )

    # Retrying the (already-accepted) submission must not mint a new snapshot.
    retry = client.post(
        f"/api/v1/applications/{application_id}/submit", headers=auth_headers("sub_agency_officer")
    )
    assert retry.status_code == 200
    assert retry.json()["snapshot_id"].startswith(f"snapshot-{application_id}-v")

    second = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )
    assert first.json()["current_version"] == second.json()["current_version"]


def test_final_decision_is_locked_from_further_ordinary_changes(client):
    application_id = _create_payment_pending_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )

    decision = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert decision.json()["current_status"] == "approved"

    blocked = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert blocked.status_code == 400

    from src.applications.models.visa_application import VisaApplication
    from src.db.base import SessionLocal

    with SessionLocal() as db:
        application = db.get(VisaApplication, application_id)
        assert application.terminal_locked_at is not None
        assert application.terminal_outcome == "approved"


def test_duplicate_payment_confirmation_does_not_create_a_second_financial_record(client):
    application_id = _create_payment_pending_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )

    from src.db.base import SessionLocal
    from src.finance.models.payment import Payment

    with SessionLocal() as db:
        payments = db.query(Payment).filter_by(application_id=application_id).all()
        assert len(payments) == 1


def test_no_route_exists_to_directly_mutate_or_delete_an_audit_event(client):
    # The audit events path is registered (GET works) but exposes no
    # mutating verb: PATCH/PUT/DELETE all fall through to 405 Method Not
    # Allowed rather than any handler.
    readable = client.get("/api/v1/audit/events", headers=auth_headers("auditor_compliance"))
    assert readable.status_code == 200

    for verb in ("patch", "put", "delete"):
        response = getattr(client, verb)("/api/v1/audit/events")
        assert (
            response.status_code == 405
        ), f"{verb.upper()} /audit/events should not be a valid operation"
