"""API routing structure (T025): authentication, authorization, idempotency,
and audit are applied per-route via src/api/deps.py dependencies and each
service's own audit_middleware call. This module aggregates all module
routers behind a single versioned prefix.
"""

from fastapi import APIRouter

from src.api.applications_routes import router as applications_router
from src.api.audit_routes import router as audit_router
from src.api.documents_routes import router as documents_router
from src.api.finance_routes import router as finance_router
from src.api.main_agency_routes import router as main_agency_router
from src.api.notifications_routes import router as notifications_router
from src.api.payment_immigration_routes import router as payment_immigration_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(applications_router)
api_router.include_router(documents_router)
api_router.include_router(finance_router)
api_router.include_router(main_agency_router)
api_router.include_router(payment_immigration_router)
api_router.include_router(notifications_router)
api_router.include_router(audit_router)
