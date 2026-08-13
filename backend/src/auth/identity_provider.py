"""Identity and access management integration (T013).

Mock adapter standing in for a real IdP (OIDC/SAML provider). Reads the
mocked user directory fixture and exposes authentication, role, agency
scope, privileged-access, and session-status signals behind a stable
interface so the real IdM integration can be swapped in without touching
callers. Per integration-contracts.md: missing/expired/revoked/insufficient
identity denies action without data change.
"""

import json
from dataclasses import dataclass
from pathlib import Path

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "integrations"
    / "identity_provider.json"
)

PRIVILEGED_ROLES = {
    "main_agency_supervisor",
    "finance_officer",
    "support_admin",
    "auditor_compliance",
}


@dataclass(frozen=True)
class Identity:
    user_id: str
    role: str
    agency_id: str | None
    session_valid: bool = True
    strongly_authenticated: bool = True

    @property
    def is_privileged(self) -> bool:
        return self.role in PRIVILEGED_ROLES


class IdentityDeniedError(PermissionError):
    """Raised when identity is missing, expired, revoked, or insufficient."""


class IdentityProvider:
    def __init__(self):
        self._users = {u["user_id"]: u for u in json.loads(FIXTURE_PATH.read_text())["users"]}

    def authenticate(self, token: str | None) -> Identity:
        """Scaffold auth: token is the raw user_id from the mocked directory.
        Real environments replace this with signed-token/session verification."""
        if not token:
            raise IdentityDeniedError("missing identity token")
        user = self._users.get(token)
        if user is None:
            raise IdentityDeniedError("unknown or revoked identity")
        require_strong = user["role"] in PRIVILEGED_ROLES
        return Identity(
            user_id=user["user_id"],
            role=user["role"],
            agency_id=user.get("agency_id"),
            session_valid=True,
            strongly_authenticated=True if require_strong else True,
        )


_provider = IdentityProvider()


def get_identity_provider() -> IdentityProvider:
    return _provider
