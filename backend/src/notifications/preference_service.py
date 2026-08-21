"""Notification preference management honoring mandatory operational/legal
notices (T149).

Preferences are stored on Applicant.contact_details (already a free-form
JSON column) under a "notification_preferences" key rather than a new
table, since the feature only needs a channel choice and an opt-out event
list per applicant. Mandatory events (policy.mandatory_notification_events)
always proceed regardless of preference.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.applicant import Applicant
from src.config import get_policy_config

DEFAULT_CHANNEL = "email"


@dataclass(frozen=True)
class NotificationPreference:
    channel: str
    opted_out_events: tuple[str, ...]


class ApplicantNotFoundError(ValueError):
    pass


def get_preference(db: Session, applicant_id: str) -> NotificationPreference:
    applicant = db.get(Applicant, applicant_id)
    if applicant is None:
        raise ApplicantNotFoundError(applicant_id)
    stored = (applicant.contact_details or {}).get("notification_preferences", {})
    return NotificationPreference(
        channel=stored.get("channel", DEFAULT_CHANNEL),
        opted_out_events=tuple(stored.get("opted_out_events", [])),
    )


def set_preference(
    db: Session, applicant_id: str, channel: str, opted_out_events: list[str]
) -> NotificationPreference:
    applicant = db.get(Applicant, applicant_id)
    if applicant is None:
        raise ApplicantNotFoundError(applicant_id)

    policy = get_policy_config()
    # Mandatory operational/legal notices can never be opted out of (FR-027).
    allowed_opt_outs = [
        e for e in opted_out_events if e not in policy.mandatory_notification_events
    ]

    contact_details = dict(applicant.contact_details or {})
    contact_details["notification_preferences"] = {
        "channel": channel,
        "opted_out_events": allowed_opt_outs,
    }
    applicant.contact_details = contact_details
    db.commit()

    return NotificationPreference(channel=channel, opted_out_events=tuple(allowed_opt_outs))


def is_event_allowed(preference: NotificationPreference, event_type: str) -> bool:
    policy = get_policy_config()
    if event_type in policy.mandatory_notification_events:
        return True
    return event_type not in preference.opted_out_events
