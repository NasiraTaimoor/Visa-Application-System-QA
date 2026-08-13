"""Document screening adapter: type/size/quality/integrity/password/malware
checks (T069). Scaffold implementation performs deterministic checks against
the content and filename so tests are reproducible; a real environment swaps
this for the document screening provider behind the same interface, keyed by
backend/tests/fixtures/integrations/document_screening.json's mocked outcome
shapes.
"""

from dataclasses import dataclass
from pathlib import Path

from src.config import get_policy_config

# Scaffold-only markers so tests can force specific rejection categories
# without a real screening provider.
MALWARE_MARKER = b"MALWARE_TEST_MARKER"
PASSWORD_MARKER = b"PASSWORD_PROTECTED_TEST_MARKER"
CORRUPT_MARKER = b"CORRUPT_TEST_MARKER"


@dataclass(frozen=True)
class ScreeningResult:
    accepted: bool
    screening_status: str  # accepted | rejected
    reject_reason_category: str | None = (
        None  # type | size | quality | integrity | password | security
    )
    protected_diagnostic_reference: str | None = None


def screen_document(document_type: str, filename: str, content: bytes) -> ScreeningResult:
    policy = get_policy_config()

    if not content:
        return _reject("integrity", "empty or unreadable file")

    if len(content) > policy.document_max_size_bytes:
        return _reject("size", "file exceeds the maximum allowed size")

    extension = Path(filename).suffix.lower()
    if extension not in policy.document_allowed_extensions:
        return _reject("type", "unsupported file format")

    if document_type not in policy.document_requirements:
        return _reject("type", "document type is not recognized for any visa type")

    if MALWARE_MARKER in content:
        return _reject("security", "failed malware/security screening")

    if PASSWORD_MARKER in content:
        return _reject("password", "document is password protected")

    if CORRUPT_MARKER in content:
        return _reject("integrity", "document content is corrupted")

    return ScreeningResult(accepted=True, screening_status="accepted")


def _reject(category: str, reason: str) -> ScreeningResult:
    import uuid

    return ScreeningResult(
        accepted=False,
        screening_status="rejected",
        reject_reason_category=category,
        protected_diagnostic_reference=str(uuid.uuid4()),
    )
