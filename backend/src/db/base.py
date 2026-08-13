"""Transactional application data store schema/engine (T010).

Separate from the audit/event store (see src/audit/store) so that audit
writes remain append-only and cannot be affected by transactional rollback
semantics of case data.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import get_settings


class Base(DeclarativeBase):
    pass


def build_engine(url: str | None = None):
    settings = get_settings()
    return create_engine(
        url or settings.database_url,
        connect_args=(
            {"check_same_thread": False} if "sqlite" in (url or settings.database_url) else {}
        ),
    )


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables. Alembic migrations (backend/alembic) own schema
    evolution in real environments; this is used for the scaffold/tests."""
    from src.agencies.models import (
        agency,  # noqa: F401
        processing_task,  # noqa: F401
    )
    from src.applications.idempotency import idempotency_store  # noqa: F401
    from src.applications.models import (  # noqa: F401
        applicant,
        passport,
        status_event,
        submission,
        visa_application,
    )
    from src.compliance.models import consent_retention_policy  # noqa: F401
    from src.documents.models import document  # noqa: F401
    from src.finance.models import payment, wallet_ledger_event  # noqa: F401
    from src.integrations.models import external_case_response  # noqa: F401
    from src.notifications.models import notification  # noqa: F401
    from src.ocr.models import ocr_result  # noqa: F401
    from src.recovery import outbox_queue  # noqa: F401
    from src.recovery.models import error_record  # noqa: F401
    from src.validation.models import validation_finding  # noqa: F401

    Base.metadata.create_all(bind=engine)
