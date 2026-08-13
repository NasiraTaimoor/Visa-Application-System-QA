"""Contradictory/unmatched immigration status quarantine (T128).
Traceability: TS-FR-021/TC-FR-021 (E-017 pattern applied to immigration
updates), BR-013."""

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_contradictory_update_is_quarantined_without_changing_status(client):
    application_id = _create_payment_pending_application(client, legal_name="IMM_CONTRADICTORY Doe")
    client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )

    response = client.post(
        f"/api/v1/applications/{application_id}/immigration/update",
        headers=auth_headers("gdrfa_immigration_liaison"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["quarantined"] is True
    # The handoff into immigration_processing still occurs (external
    # reference/payment prerequisites are satisfied); only the contradictory
    # status value itself is withheld from changing the case further.
    assert body["current_status"] == "immigration_processing"

    from src.db.base import SessionLocal
    from src.integrations.models.external_case_response import ExternalCaseResponse

    with SessionLocal() as db:
        quarantined = (
            db.query(ExternalCaseResponse)
            .filter_by(application_id=application_id, matched_status="unmatched")
            .all()
        )
        assert len(quarantined) == 1
        assert quarantined[0].quarantine_reason is not None
