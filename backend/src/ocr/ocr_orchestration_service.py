"""OCR orchestration service, gated on passed screening (T071).

Mocked OCR provider adapter reads backend/tests/fixtures/integrations/ocr_provider.json.
Scaffold-only content markers select a response variant so tests are
deterministic without a real OCR vendor.
"""

import json
from pathlib import Path

from sqlalchemy.orm import Session

from src.documents.models.document import Document
from src.ocr.models.ocr_result import OcrResult

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "integrations"
    / "ocr_provider.json"
)

LOW_CONFIDENCE_MARKER = b"OCR_LOW_CONFIDENCE"
FAILURE_MARKER = b"OCR_FAIL"


class DocumentNotScreenedError(ValueError):
    pass


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def _select_response(content: bytes) -> dict:
    fixture = _load_fixture()
    if FAILURE_MARKER in content:
        return fixture["failure_response"]
    if LOW_CONFIDENCE_MARKER in content:
        return {**fixture["default_response"], **fixture["low_confidence_response"]}
    return fixture["default_response"]


def run_ocr(db: Session, document: Document, content: bytes) -> OcrResult:
    if document.screening_status != "accepted":
        raise DocumentNotScreenedError("OCR cannot run on a document that has not passed screening")

    response = _select_response(content)
    result = OcrResult(
        document_id=document.document_id,
        extraction_status=response["extraction_status"],
        extracted_fields=response.get("extracted_fields", {}),
        confidence_by_field=response.get("confidence_by_field", {}),
        overall_confidence=response.get("overall_confidence"),
        warning_flags=response.get("warning_flags", []),
        source_payload_reference=response.get("failure_reason"),
    )
    db.add(result)
    db.flush()
    return result
