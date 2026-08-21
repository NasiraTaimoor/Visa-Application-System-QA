"""Draft save/interrupt/resume/missing-item journey (T038).

Traceability: TS-FR-001-TS-FR-004, TC-FR-001-TC-FR-004 (User Story 1).
"""

from tests.conftest import auth_headers


def test_full_intake_journey_save_interrupt_resume(client):
    create = client.post(
        "/api/v1/applications",
        json={
            "visa_type": "student",
            "owning_sub_agency_id": "sub-agency-001",
            "consent_given": True,
        },
        headers=auth_headers("applicant"),
    )
    assert create.status_code == 200
    application_id = create.json()["application_id"]
    assert create.json()["current_status"] == "draft_created"

    save = client.patch(
        f"/api/v1/applications/{application_id}",
        json={
            "expected_version": 1,
            "applicant_fields": {"legal_name": "Jane Doe", "nationality": "GBR"},
            "passport_fields": {"passport_number": "P1234567"},
        },
        headers=auth_headers("applicant"),
    )
    assert save.status_code == 200
    assert save.json()["current_version"] == 2
    missing_after_save = save.json()["missing_items"]
    assert "applicant.legal_name" not in missing_after_save
    assert (
        "applicant.date_of_birth" in missing_after_save
    )  # simulated interruption before completion

    # simulate session interruption, then resume
    resumed = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )
    assert resumed.status_code == 200
    assert resumed.json()["current_status"] == "draft_created"
    assert resumed.json()["applicant"]["legal_name"] == "Jane Doe"
    assert set(resumed.json()["missing_items"]) == set(missing_after_save)
