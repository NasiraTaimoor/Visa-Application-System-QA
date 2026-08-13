"""Complete audit trail across intake, submission, payment, and decision
actions (T160). Traceability: TS-FR-029-034/TC-FR-029-034, TS-FR-036,
TS-FR-039-041, AC-008, SC-007."""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_full_lifecycle_produces_a_complete_audit_trail(client):
    application_id = _create_payment_pending_application(client)
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )

    response = client.get(
        f"/api/v1/audit/events?application_id={application_id}",
        headers=auth_headers("auditor_compliance"),
    )
    assert response.status_code == 200
    actions = [e["action"] for e in response.json()["events"]]

    expected_actions = [
        "application.create",
        "application.update_intake",
        "document.upload",
        "application.validate",
        "wallet.verify",
        "submission.submit_main_agency",
        "case.claim",
        "case.readiness_approve",
        "gdrfa.submit",
        "payment.confirm",
        "immigration.update",
    ]
    for expected in expected_actions:
        assert expected in actions, f"missing audit action: {expected}"

    # Every event carries the mandatory audit fields (BR-036).
    for event in response.json()["events"]:
        assert event["actor_or_service_id"]
        assert event["role"]
        assert event["timestamp"]
        assert event["affected_case_or_record"] == application_id
        assert event["outcome"]
        assert event["source"]
        assert event["correlation_reference"]
