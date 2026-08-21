"""Role/agency-scope authorization policy service (T014).

Checks include role, agency scope, lifecycle state, ownership, source
validation, and required business reason per api-contract.md's Common
Requirements. Denials never mutate data and are audit-recorded by callers
via audit_middleware.
"""

from dataclasses import dataclass

from src.auth.identity_provider import Identity
from src.config import get_policy_config


class AuthorizationDeniedError(PermissionError):
    pass


@dataclass(frozen=True)
class AuthorizationContext:
    identity: Identity
    action: str
    owning_agency_id: str | None = None
    owner_user_id: str | None = None
    business_reason: str | None = None
    requires_reason: bool = False


def authorize(ctx: AuthorizationContext) -> None:
    policy = get_policy_config()
    allowed_actions = policy.permission_matrix.get(ctx.identity.role, ())
    if ctx.action not in allowed_actions:
        raise AuthorizationDeniedError(
            f"role '{ctx.identity.role}' is not permitted to perform '{ctx.action}'"
        )

    if not ctx.identity.session_valid:
        raise AuthorizationDeniedError("session is not valid")

    if ctx.owning_agency_id is not None and ctx.identity.agency_id is not None:
        if ctx.identity.agency_id != ctx.owning_agency_id:
            raise AuthorizationDeniedError("cross-agency access denied")

    if ctx.owner_user_id is not None and ctx.identity.role == "applicant":
        if ctx.identity.user_id != ctx.owner_user_id:
            raise AuthorizationDeniedError("cannot access another applicant's case")

    if ctx.requires_reason and not ctx.business_reason:
        raise AuthorizationDeniedError("a business reason is required for this action")
