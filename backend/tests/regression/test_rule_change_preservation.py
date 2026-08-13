"""Regression suite for in-progress case preservation during rule/fee/
routing/integration changes, covering FR-035 (T177). Traceability:
TS-FR-035/TC-FR-035, SC-009.
"""

from dataclasses import replace

from tests.conftest import auth_headers


def _create_draft_with_data(client):
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
    client.patch(
        f"/api/v1/applications/{application_id}",
        json={
            "expected_version": 1,
            "applicant_fields": {
                "legal_name": "Jane Doe",
                "date_of_birth": "1990-05-14",
                "nationality": "GBR",
            },
            "passport_fields": {
                "passport_number": "P1234567",
                "issuing_country": "GBR",
                "issue_date": "2020-01-01",
                "expiry_date": "2030-05-13",
            },
        },
        headers=auth_headers("applicant"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "passport_bio_page"},
        files={"file": ("passport.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers("applicant"),
    )
    client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={"document_type": "photo"},
        files={"file": ("photo.jpg", b"fake bytes", "image/jpeg")},
        headers=auth_headers("applicant"),
    )
    return application_id


def test_document_rule_change_preserves_data_and_flags_revalidation(client, monkeypatch):
    """A new document-requirement rule (e.g. tourist visas now also require
    a sponsor letter) must not lose, duplicate, or misroute the in-progress
    application; the case simply surfaces the newly-required item on the
    next validation run, exactly like any other missing item."""
    application_id = _create_draft_with_data(client)

    ready = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    assert ready.json()["current_status"] == "ready_for_sub_agency_review"

    import src.applications.intake.completeness_service as completeness_service
    import src.validation.validation_engine as validation_engine
    from src.config.policy import get_policy_config

    original_policy = get_policy_config()
    changed_requirements = dict(original_policy.document_requirements)
    changed_requirements["sponsor_letter"] = (*changed_requirements["sponsor_letter"], "tourist")
    changed_policy = replace(original_policy, document_requirements=changed_requirements)

    monkeypatch.setattr(completeness_service, "get_policy_config", lambda: changed_policy)
    monkeypatch.setattr(validation_engine, "get_policy_config", lambda: changed_policy)

    revalidated = client.post(
        f"/api/v1/applications/{application_id}/validate", headers=auth_headers("applicant")
    )
    body = revalidated.json()

    # The case itself is untouched: same id, same prior data, not deleted or duplicated.
    resumed = client.get(
        f"/api/v1/applications/{application_id}/resume", headers=auth_headers("applicant")
    )
    assert resumed.status_code == 200
    assert resumed.json()["applicant"]["legal_name"] == "Jane Doe"

    # The new rule is surfaced as a fresh, clearly attributable finding rather
    # than silently blocking or corrupting the case.
    assert body["is_ready"] is False
    assert any(
        f["affected_field_or_document"] == "document.sponsor_letter" for f in body["findings"]
    )
    # Status does not regress or corrupt: the case stays exactly where it was,
    # with the new requirement visible as an actionable finding instead.
    assert body["current_status"] == "ready_for_sub_agency_review"
