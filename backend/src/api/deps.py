"""Shared FastAPI dependencies: authentication, correlation reference, and
idempotency-key extraction applied across all routers (part of T025)."""

import uuid

from fastapi import Header, HTTPException

from src.auth.identity_provider import Identity, IdentityDeniedError, get_identity_provider


def get_identity(authorization: str | None = Header(default=None)) -> Identity:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    try:
        return get_identity_provider().authenticate(token)
    except IdentityDeniedError as exc:
        raise HTTPException(status_code=401, detail="authentication required") from exc


def get_correlation_reference(x_correlation_reference: str | None = Header(default=None)) -> str:
    return x_correlation_reference or str(uuid.uuid4())


def get_idempotency_key(
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
) -> str | None:
    return idempotency_key
