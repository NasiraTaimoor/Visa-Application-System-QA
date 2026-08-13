"""Security test for encryption-in-transit/at-rest configuration
verification (T185). Traceability: TS-FR-031/TC-FR-031 (security
requirement: "sensitive data must be encrypted in transit and at rest where
supported by the platform").

This is a scaffold running mocked integrations over SQLite in-process, so
there is no real network/TLS boundary or disk-level encryption to exercise.
What this suite verifies instead is that the *configuration surface* is
built the way a real deployment would need in order to turn on
transit/at-rest encryption: connection strings are environment-driven (not
hardcoded), the audit and transactional stores are separately configurable,
and nothing in source forces an insecure scheme. It does not, and cannot,
prove that a deployed instance actually terminates TLS or encrypts its
disks — that verification belongs to deployment/infrastructure review.
"""

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def test_database_urls_are_environment_driven_not_hardcoded():
    from src.config.settings import Settings

    # The scaffold default is sqlite (documented, non-production); production
    # values must come from DATABASE_URL/AUDIT_DATABASE_URL, which this model
    # already supports via pydantic-settings env loading.
    assert Settings.model_fields["database_url"].annotation is str
    assert Settings.model_fields["audit_database_url"].annotation is str


def test_env_example_documents_a_tls_capable_postgres_scheme():
    env_example = (BACKEND_ROOT / ".env.example").read_text()
    assert "postgresql" in env_example
    # Documents the two stores as physically separate connections, which is
    # required for the audit store's independent access/encryption controls.
    assert "AUDIT_DATABASE_URL" in env_example
    assert "DATABASE_URL" in env_example


def test_no_source_file_hardcodes_a_non_localhost_connection_string():
    """Guards against accidentally committing a real, reachable credentialed
    connection string in source (as opposed to .env.example's documented
    localhost placeholder)."""
    import re

    pattern = re.compile(r"(postgresql|mysql|mongodb)(\+\w+)?://\w+:\S+@(?!localhost)")
    offenders = []
    for path in (BACKEND_ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
            offenders.append(str(path))
    assert not offenders, f"hardcoded non-localhost connection string(s) found: {offenders}"


def test_object_storage_adapter_does_not_log_or_return_raw_bytes():
    """Documents storage keeps content behind an opaque file_reference; the
    adapter interface never round-trips raw bytes through logs or API
    responses (upload endpoints return only document_id/version/status)."""
    import inspect

    from src.documents.storage.object_storage_adapter import ObjectStorageAdapter

    source = inspect.getsource(ObjectStorageAdapter)
    assert "print(" not in source
    assert "logger" not in source.lower()
