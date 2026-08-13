"""Structured logging with secret/PII masking (T027)."""

import json
import logging
import re
import sys

MASK_PATTERNS = [
    (
        re.compile(
            r'"?(password|secret|token|api_key|jwt|authorization)"?\s*[:=]\s*"?[^",}\s]+', re.I
        ),
        r'"\1": "***MASKED***"',
    ),
    (re.compile(r"\b\d{9,}\b"), "***MASKED_ID***"),  # coarse passport/id number mask
]


def _mask(value: str) -> str:
    for pattern, replacement in MASK_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


class MaskingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Mask the raw message *before* JSON-encoding it: json.dumps escapes
        # internal quotes as `\"`, which breaks the mask patterns' literal
        # `"` matching and would let secrets pass through unmasked.
        base = {
            "level": record.levelname,
            "logger": record.name,
            "message": _mask(record.getMessage()),
        }
        if hasattr(record, "correlation_reference"):
            base["correlation_reference"] = record.correlation_reference
        return json.dumps(base)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("visa_application")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(MaskingFormatter())
        logger.addHandler(handler)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("visa_application")
