from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from .base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a transactional-store session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for use outside request scope (services, tests, workers)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
