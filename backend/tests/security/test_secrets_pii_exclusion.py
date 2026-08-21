"""Security test for secrets/PII exclusion from logs, notifications,
exports, and client bundles (T184). Traceability: TS-FR-031/TC-FR-031,
FR-031, security requirement "secrets, credentials, tokens... must never be
exposed in source control, logs, notification content, exports, or
client-delivered bundles."
"""

import json
import logging

from tests.conftest import auth_headers
from tests.contract.test_record_payment_event import _create_payment_pending_application


def test_error_responses_never_include_stack_traces_or_internal_details(client):
    # Trigger an internal error path (stale version) and confirm the body is safe.
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
    response = client.patch(
        f"/api/v1/applications/{application_id}",
        json={"expected_version": 999, "applicant_fields": {}},
        headers=auth_headers("applicant"),
    )
    assert response.status_code == 400
    body = response.json()
    assert set(body.keys()) == {"message", "diagnostic_reference"}
    lowered = json.dumps(body).lower()
    for forbidden in ("traceback", 'file "', "site-packages", "raise ", "exception"):
        assert forbidden not in lowered


def test_log_formatter_masks_secrets_and_long_numeric_identifiers():
    from src.observability.logging import MaskingFormatter

    record = logging.LogRecord(
        name="visa_application",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='processing token="abc123secretvalue" for passport 123456789012',
        args=(),
        exc_info=None,
    )
    formatted = MaskingFormatter().format(record)
    assert "abc123secretvalue" not in formatted
    assert "123456789012" not in formatted
    assert "MASKED" in formatted


def test_notification_model_never_stores_raw_personal_data_fields():
    """Structural check: the Notification table has no column for legal
    name, passport number, or any other raw personal data — only
    recipient_category/channel/classification metadata (BR-012)."""
    from src.notifications.models.notification import Notification

    columns = {c.name for c in Notification.__table__.columns}
    forbidden = {"legal_name", "passport_number", "date_of_birth", "email", "phone"}
    assert not (forbidden & columns)


def test_audit_event_never_stores_raw_personal_data_fields():
    from src.audit.models.audit_event import AuditEvent

    columns = {c.name for c in AuditEvent.__table__.columns}
    forbidden = {"legal_name", "passport_number", "date_of_birth"}
    assert not (forbidden & columns)


def test_settings_defaults_are_clearly_marked_as_non_production_placeholders():
    from src.config.settings import Settings

    settings = Settings()
    assert "not-a-real-secret" in settings.identity_provider_jwt_secret
    assert "not-a-real-secret" in settings.notification_gateway_api_key


def test_env_example_file_contains_no_real_looking_secret_values():
    from pathlib import Path

    env_example = (Path(__file__).resolve().parent.parent.parent / ".env.example").read_text()
    for line in env_example.splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if "SECRET" in key or "KEY" in key:
            assert value.strip() in (
                "change-me-in-real-environment",
            ), f"{key} looks like a real secret value"


def test_payment_confirmation_response_does_not_leak_provider_secrets(client):
    application_id = _create_payment_pending_application(client)
    response = client.post(
        f"/api/v1/applications/{application_id}/payment/confirm",
        headers=auth_headers("finance_officer"),
    )
    body_text = json.dumps(response.json())
    for forbidden in ("api_key", "secret", "password"):
        assert forbidden not in body_text.lower()
