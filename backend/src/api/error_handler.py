"""Centralized error handling with safe user-facing messages and protected
diagnostic references (T026). No stack traces, secrets, tokens, or internal
endpoints ever reach the client per data-model.md Error Record rules."""

import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.applications.idempotency.idempotency_store import DuplicateRequestReplay
from src.applications.workflow.state_machine import InvalidTransitionError
from src.auth.authorization_policy import AuthorizationDeniedError
from src.auth.identity_provider import IdentityDeniedError
from src.observability.logging import get_logger


def _safe_error(request: Request, status_code: int, message: str) -> JSONResponse:
    diagnostic_reference = str(uuid.uuid4())
    get_logger().error(
        "request_error status=%s path=%s diagnostic_reference=%s",
        status_code,
        request.url.path,
        diagnostic_reference,
    )
    return JSONResponse(
        status_code=status_code,
        content={"message": message, "diagnostic_reference": diagnostic_reference},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(IdentityDeniedError)
    async def _identity_denied(request: Request, exc: IdentityDeniedError):
        return _safe_error(request, 401, "Authentication is required or has expired.")

    @app.exception_handler(AuthorizationDeniedError)
    async def _authorization_denied(request: Request, exc: AuthorizationDeniedError):
        return _safe_error(request, 403, "You are not authorized to perform this action.")

    @app.exception_handler(InvalidTransitionError)
    async def _invalid_transition(request: Request, exc: InvalidTransitionError):
        return _safe_error(request, 409, "This action is not valid for the case's current status.")

    @app.exception_handler(DuplicateRequestReplay)
    async def _duplicate_replay(request: Request, exc: DuplicateRequestReplay):
        return JSONResponse(
            status_code=200,
            content={
                "message": "Request already processed.",
                "result_reference": exc.existing_result_reference,
            },
        )

    @app.exception_handler(ValueError)
    async def _value_error(request: Request, exc: ValueError):
        return _safe_error(request, 400, "The request could not be processed.")

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        return _safe_error(request, 500, "An unexpected error occurred. Please try again.")
