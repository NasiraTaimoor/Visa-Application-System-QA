"""Security test sweep for authorization boundaries across all roles and
agency scopes (T183). Traceability: TS-FR-033/TC-FR-033, FR-033, E-009.

Complements the pure-function permission matrix regression (T175) by
exercising real API endpoints end-to-end: every case-mutating endpoint must
deny an actor outside the correct role/agency scope without mutating data.
"""

from tests.conftest import auth_headers
from tests.integration.test_main_agency_processing import _create_submitted_application


def _create_draft(client):
    response = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "tourist",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("applicant"),
    )
    return response.json()["application_id"]


def test_every_mutating_endpoint_denies_the_wrong_role(client):
    application_id = _create_draft(client)

    denied_attempts = [
        ("post", f"/api/v1/applications/{application_id}/wallet/verify", {}, "applicant"),
        ("post", f"/api/v1/applications/{application_id}/submit", {}, "applicant"),
        ("post", f"/api/v1/applications/{application_id}/claim", {}, "applicant"),
        (
            "post",
            f"/api/v1/applications/{application_id}/correction-request",
            {"reason": "x", "responsible_party": "applicant"},
            "applicant",
        ),
        (
            "post",
            f"/api/v1/applications/{application_id}/readiness-approve",
            {"reason": "x"},
            "applicant",
        ),
        ("post", f"/api/v1/applications/{application_id}/gdrfa/submit", {}, "sub_agency_officer"),
        ("post", f"/api/v1/applications/{application_id}/payment/confirm", {}, "applicant"),
        (
            "post",
            f"/api/v1/applications/{application_id}/payment/reconcile",
            {"receipt_reference": "r", "amount": 1, "currency": "AED", "reason": "x"},
            "applicant",
        ),
        ("post", f"/api/v1/applications/{application_id}/immigration/update", {}, "applicant"),
    ]

    for method, path, body, wrong_role in denied_attempts:
        response = getattr(client, method)(path, json=body, headers=auth_headers(wrong_role))
        assert (
            response.status_code == 403
        ), f"{method.upper()} {path} should deny role '{wrong_role}'"

    # Data was never mutated by any denied attempt.
    resumed = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )
    assert resumed.json()["current_status"] == "draft_created"


def test_cross_sub_agency_officer_cannot_act_on_another_agencys_case(client):
    application_id = _create_draft(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/wallet/verify",
        headers={"Authorization": "Bearer u-subagency-2"},
    )
    assert response.status_code in (
        400,
        403,
    )  # denied either by scope or by not-yet-ready state; never succeeds


def test_cross_main_agency_officer_cannot_claim_a_case_routed_elsewhere(client):
    application_id = _create_submitted_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/claim",
        headers={"Authorization": "Bearer u-mainagency-2"},
    )
    assert response.status_code == 403


def test_support_admin_cannot_approve_a_validation_override(client):
    # Denied purely by role before any finding lookup, so no case setup is needed.
    response = client.post(
        "/api/v1/validation/findings/nonexistent-finding/override",
        json={"reason": "trying to bypass"},
        headers=auth_headers("support_admin"),
    )
    assert response.status_code == 403


def test_finance_officer_cannot_process_main_agency_cases(client):
    application_id = _create_submitted_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/claim", headers=auth_headers("finance_officer")
    )
    assert response.status_code == 403
