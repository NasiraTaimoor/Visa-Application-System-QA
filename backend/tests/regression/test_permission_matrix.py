"""Regression suite for action-level permission matrix enforcement across
all roles (T175). Traceability: TS-FR-040/TC-FR-040, FR-040.

For every role, every action granted to that role must authorize, and every
action granted only to *other* roles must be denied for it.
"""

import pytest
from src.auth.authorization_policy import AuthorizationContext, AuthorizationDeniedError, authorize
from src.auth.identity_provider import Identity
from src.config import get_policy_config

POLICY = get_policy_config()
ALL_ROLES = sorted(POLICY.permission_matrix.keys())
ALL_ACTIONS = sorted(
    {action for actions in POLICY.permission_matrix.values() for action in actions}
)


def _identity(role: str) -> Identity:
    return Identity(user_id=f"test-{role}", role=role, agency_id=None)


@pytest.mark.parametrize("role", ALL_ROLES)
def test_role_can_perform_every_action_granted_to_it(role):
    for action in POLICY.permission_matrix[role]:
        authorize(AuthorizationContext(identity=_identity(role), action=action))


@pytest.mark.parametrize("role", ALL_ROLES)
def test_role_cannot_perform_actions_not_granted_to_it(role):
    not_granted = set(ALL_ACTIONS) - set(POLICY.permission_matrix[role])
    for action in not_granted:
        with pytest.raises(AuthorizationDeniedError):
            authorize(AuthorizationContext(identity=_identity(role), action=action))


def test_unknown_role_is_denied_every_action():
    identity = _identity("not_a_real_role")
    for action in ALL_ACTIONS:
        with pytest.raises(AuthorizationDeniedError):
            authorize(AuthorizationContext(identity=identity, action=action))


def test_invalid_session_is_always_denied_even_for_a_granted_action():
    identity = Identity(user_id="u-1", role="applicant", agency_id=None, session_valid=False)
    granted_action = next(iter(POLICY.permission_matrix["applicant"]))
    with pytest.raises(AuthorizationDeniedError):
        authorize(AuthorizationContext(identity=identity, action=granted_action))


def test_cross_agency_access_is_denied_even_for_a_granted_action():
    identity = Identity(user_id="u-1", role="sub_agency_officer", agency_id="sub-agency-001")
    with pytest.raises(AuthorizationDeniedError):
        authorize(
            AuthorizationContext(
                identity=identity, action="wallet:verify", owning_agency_id="sub-agency-999"
            )
        )


def test_reason_required_action_is_denied_without_a_reason():
    identity = _identity("main_agency_supervisor")
    with pytest.raises(AuthorizationDeniedError):
        authorize(
            AuthorizationContext(
                identity=identity, action="validation:override_approve", requires_reason=True
            )
        )
