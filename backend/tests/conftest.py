"""Shared backend test harness (T031): isolated SQLite database per test,
FastAPI TestClient, and identity header helpers for each role fixture in
tests/fixtures/integrations/identity_provider.json.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault(
    "DATABASE_URL", "sqlite:///" + os.path.join(tempfile.gettempdir(), "visa_app_test.db")
)
os.environ.setdefault(
    "AUDIT_DATABASE_URL",
    "sqlite:///" + os.path.join(tempfile.gettempdir(), "visa_app_audit_test.db"),
)


@pytest.fixture()
def db_session():

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    import src.db.base as db_base

    db_base.engine = engine
    db_base.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    from src.db.base import init_db

    init_db()
    session = db_base.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def audit_session():
    from src.audit.store import base as audit_base

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    audit_base.audit_engine = engine
    audit_base.AuditSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    audit_base.init_audit_db()
    session = audit_base.AuditSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Fresh in-memory database per test. Rebinds the *existing* SessionLocal/
    AuditSessionLocal objects in place (sessionmaker.configure) rather than
    replacing them, since service modules imported `from ...base import
    SessionLocal` at import time and only a same-object mutation is visible
    to those already-bound references. StaticPool is required (not just
    check_same_thread=False): FastAPI runs sync `def` route handlers in a
    threadpool, and plain sqlite:///:memory: gives each connection/thread its
    own separate in-memory database, so tables created here would be
    invisible to the request thread without a single shared connection."""
    import src.audit.store.base as audit_base
    import src.db.base as db_base

    db_engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    db_base.engine = db_engine
    db_base.SessionLocal.configure(bind=db_engine)
    db_base.init_db()

    audit_engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    audit_base.audit_engine = audit_engine
    audit_base.AuditSessionLocal.configure(bind=audit_engine)
    audit_base.init_audit_db()

    from src.main import app, seed_reference_data

    seed_reference_data()

    return TestClient(app)


ROLE_TOKENS = {
    "applicant": "u-applicant-1",
    "sub_agency_officer": "u-subagency-1",
    "main_agency_case_officer": "u-mainagency-1",
    "main_agency_supervisor": "u-supervisor-1",
    "finance_officer": "u-finance-1",
    "support_admin": "u-support-1",
    "auditor_compliance": "u-audit-1",
    "gdrfa_immigration_liaison": "u-gdrfa-1",
    "system_service": "u-system-1",
}


def auth_headers(role: str) -> dict:
    return {"Authorization": f"Bearer {ROLE_TOKENS[role]}"}
