"""Immutable audit/event store schema, separate from the transactional
application data store (T011). Deliberately isolated engine/session so audit
writes are never mixed with case-data transactions and cannot be rolled back
by unrelated application logic.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import get_settings


class AuditBase(DeclarativeBase):
    pass


def _build_audit_engine():
    settings = get_settings()
    url = settings.audit_database_url
    return create_engine(url, connect_args={"check_same_thread": False} if "sqlite" in url else {})


audit_engine = _build_audit_engine()
AuditSessionLocal = sessionmaker(bind=audit_engine, autoflush=False, autocommit=False)


def init_audit_db() -> None:
    from src.audit.models import audit_event  # noqa: F401

    AuditBase.metadata.create_all(bind=audit_engine)


def get_audit_db() -> Generator[Session, None, None]:
    db = AuditSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def audit_session_scope() -> Generator[Session, None, None]:
    db = AuditSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
