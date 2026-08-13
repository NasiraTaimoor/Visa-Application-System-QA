"""Immigration processing through action-required to final decision and
terminal lock (T127). Traceability: TS-FR-024/TC-FR-024, BR-011, E-013."""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_action_required_then_final_decision_locks_the_case(client):
    application_id = _create_payment_pending_application(
        client, legal_name="IMM_ACTION_REQUIRED Doe"
    )
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )

    first = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert first.status_code == 200
    body = first.json()
    assert body["response_type"] == "action_required"
    assert body["current_status"] == "immigration_processing"

    # Applicant provides the requested clarification; the case is now clear for a decision.
    patch = client.patch(
        f"/api/v1/applications/{application_id}",
        json={"expected_version": 2, "applicant_fields": {"legal_name": "Jane Doe"}},
        headers=auth_headers("applicant"),
    )
    assert patch.status_code == 200

    second = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert second.status_code == 200
    body = second.json()
    assert body["response_type"] == "final_decision"
    assert body["current_status"] == "approved"

    # The terminal lock prevents any further ordinary update.
    third = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert third.status_code == 400
