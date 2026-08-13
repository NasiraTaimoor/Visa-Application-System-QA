"""Terminal outcome locking service preventing unauthorized changes to final
status (T135). Any permitted correction after a terminal lock is a
separately authorized, separately audited action — never a silent status
mutation through the ordinary update paths."""

from src.applications.models.visa_application import VisaApplication


class TerminalLockError(ValueError):
    pass


def ensure_not_locked(application: VisaApplication) -> None:
    if application.terminal_locked_at is not None:
        raise TerminalLockError(
            f"case '{application.application_id}' has a final decision and cannot be modified"
        )
