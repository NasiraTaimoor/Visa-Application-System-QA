"""FastAPI application entry point. Run with:
uvicorn src.main:app --reload
"""

from fastapi import FastAPI

from src.api.error_handler import register_error_handlers
from src.api.router import api_router
from src.audit.store.base import init_audit_db
from src.compliance.models.consent_retention_policy import DEFAULT_POLICIES
from src.db.base import init_db
from src.db.session import session_scope
from src.observability.logging import configure_logging


def seed_reference_data() -> None:
    from src.agencies.models.agency import Agency

    with session_scope() as db:
        if db.get(Agency, "main-agency-root") is None:
            db.add(
                Agency(
                    agency_id="main-agency-root",
                    agency_type="main_agency",
                    name="Main Agency",
                    parent_agency_id=None,
                )
            )
        if db.get(Agency, "sub-agency-001") is None:
            db.add(
                Agency(
                    agency_id="sub-agency-001",
                    agency_type="sub_agency",
                    name="Sub Agency 001",
                    parent_agency_id="main-agency-root",
                )
            )
        for policy in DEFAULT_POLICIES:
            existing = db.get(type(policy), policy.policy_id)
            if existing is None:
                db.merge(policy)


def create_app() -> FastAPI:
    configure_logging()
    init_db()
    init_audit_db()
    seed_reference_data()

    app = FastAPI(
        title="Visa Application System",
        version="0.1.0",
        description="Backend service for the Visa Application Lifecycle feature (scaffold; all "
        "external integrations mocked/stubbed).",
    )
    register_error_handlers(app)
    app.include_router(api_router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
