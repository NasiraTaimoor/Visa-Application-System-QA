from tests.conftest import auth_headers
from tests.integration.test_gdrfa_outcomes import _claim_and_approve
from tests.integration.test_main_agency_processing import _create_submitted_application


def test_recovery_tasks_lists_open_tasks_and_resolves_them(client):
    application_id = _create_submitted_application(client, legal_name="GDRFA_TIMEOUT Doe")
    _claim_and_approve(client, application_id)
    client.post(
        f"/api/v1/applications/{application_id}/gdrfa/submit",
        headers=auth_headers("main_agency_case_officer"),
    )

    listing = client.get("/api/v1/recovery/tasks", headers=auth_headers("support_admin"))
    assert listing.status_code == 200
    tasks = listing.json()["tasks"]
    assert any(t["application_id"] == application_id for t in tasks)
    task_id = next(t["task_id"] for t in tasks if t["application_id"] == application_id)

    resolve_no_reason = client.post(
        f"/api/v1/recovery/tasks/{task_id}/resolve",
        json={"business_reason": ""},
        headers=auth_headers("support_admin"),
    )
    assert resolve_no_reason.status_code == 400

    resolve = client.post(
        f"/api/v1/recovery/tasks/{task_id}/resolve",
        json={"business_reason": "liaison confirmed GDRFA retry succeeded manually"},
        headers=auth_headers("support_admin"),
    )
    assert resolve.status_code == 200
    assert resolve.json()["status"] == "resolved"
