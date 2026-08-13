"""Regression suite for lifecycle transition matrix enforcement across all
statuses (T174). Traceability: TS-FR-036/TC-FR-036, FR-036, SC-011.

Exhaustively checks state_machine.transition() against every (from, to)
status pair: allowed pairs succeed, everything else raises
InvalidTransitionError without any side effects (the function is pure).
"""

import pytest
from src.applications.workflow.state_machine import TRANSITIONS, InvalidTransitionError, transition

ALL_STATUSES = sorted(TRANSITIONS.keys())


@pytest.mark.parametrize("from_status", ALL_STATUSES)
def test_only_matrix_allowed_transitions_succeed(from_status):
    allowed = TRANSITIONS[from_status]
    for to_status in ALL_STATUSES:
        if to_status in allowed:
            result = transition(from_status, to_status)
            assert result.new_status == to_status
            assert result.previous_status == from_status
        else:
            with pytest.raises(InvalidTransitionError):
                transition(from_status, to_status)


def test_unknown_status_is_rejected():
    with pytest.raises(InvalidTransitionError):
        transition("not_a_real_status", "draft_created")


def test_every_declared_terminal_status_only_transitions_to_closed():
    from src.applications.workflow.state_machine import TERMINAL_STATUSES

    for status in TERMINAL_STATUSES:
        assert TRANSITIONS[status] <= {"closed"}
