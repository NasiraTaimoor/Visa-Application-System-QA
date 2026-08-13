import pytest
from src.applications.workflow.state_machine import InvalidTransitionError, is_terminal, transition


def test_valid_transition_draft_to_documents_pending():
    result = transition("draft_created", "documents_pending")
    assert result.new_status == "documents_pending"
    assert result.is_terminal is False


def test_invalid_transition_is_rejected_without_mutation():
    with pytest.raises(InvalidTransitionError):
        transition("draft_created", "approved")


def test_terminal_statuses_only_allow_closed():
    assert is_terminal("approved") is True
    transition("approved", "closed")
    with pytest.raises(InvalidTransitionError):
        transition("approved", "draft_created")
