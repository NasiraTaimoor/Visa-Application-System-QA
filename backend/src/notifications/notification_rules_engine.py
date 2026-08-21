"""Notification rules engine: maps lifecycle events to recipient categories
and minimal content (T147), attempts delivery through the gateway adapter
with retry tracking (T148), and honors preferences (T149).

BR-028/BR-029: retries only apply to delivery-failure outcomes and use the
baseline policy of `policy.notification_retry_limit` attempts; the scaffold
runs them synchronously (a real deployment would use the outbox/recovery
queue from Phase 2) since the mocked gateway responds immediately.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.applicant import Applicant
from src.applications.models.visa_application import VisaApplication
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.config import get_policy_config
from src.integrations.notification_gateway_adapter import attempt_delivery
from src.notifications.models.notification import Notification
from src.notifications.preference_service import get_preference, is_event_allowed

EVENT_RECIPIENTS: dict[str, tuple[str, ...]] = {
    "submission_created": ("applicant", "sub_agency"),
    "correction_requested": ("applicant",),
    "validation_failed": ("applicant",),
    "wallet_shortfall": ("sub_agency",),
    "payment_outcome": ("applicant", "finance"),
    "gdrfa_response": ("main_agency",),
    "immigration_event": ("applicant",),
    "final_decision": ("applicant", "sub_agency"),
}


@dataclass(frozen=True)
class NotificationDispatchResult:
    created: list[Notification]
    skipped_by_preference: tuple[str, ...]


def trigger_notification(
    db: Session, application_id: str, event_type: str, correlation_reference: str
) -> NotificationDispatchResult:
    policy = get_policy_config()
    application = db.get(VisaApplication, application_id)
    if application is None:
        return NotificationDispatchResult(created=[], skipped_by_preference=())

    applicant = db.get(Applicant, application.applicant_id)
    preference = get_preference(db, application.applicant_id) if applicant else None

    recipients = EVENT_RECIPIENTS.get(event_type, ())
    created: list[Notification] = []
    skipped: list[str] = []

    for recipient_category in recipients:
        if (
            recipient_category == "applicant"
            and preference is not None
            and not is_event_allowed(preference, event_type)
        ):
            skipped.append(recipient_category)
            continue

        notification = Notification(
            application_id=application_id,
            event_type=event_type,
            recipient_category=recipient_category,
            channel=(
                preference.channel
                if (preference and recipient_category == "applicant")
                else "email"
            ),
            preference_source=(
                "mandatory" if event_type in policy.mandatory_notification_events else "optional"
            ),
            message_classification="minimal",
        )
        db.add(notification)
        db.flush()

        routing_signal = applicant.legal_name or "" if applicant else ""
        attempts = 0
        delivered = False
        failure_reason = None
        while attempts < policy.notification_retry_limit:
            attempts += 1
            result = attempt_delivery(routing_signal)
            if result.delivered:
                delivered = True
                break
            failure_reason = result.failure_reason

        from datetime import datetime, timezone

        notification.attempt_count = attempts
        notification.last_attempt_at = datetime.now(timezone.utc)
        if delivered:
            notification.delivery_status = "delivered"
            notification.retry_status = None
        else:
            notification.delivery_status = "failed"
            notification.failure_reason = failure_reason
            notification.retry_status = "exhausted"

        created.append(notification)

    db.commit()
    for notification in created:
        db.refresh(notification)

    if created:
        with AuditSessionLocal() as audit_db:
            for notification in created:
                record_audit_event(
                    audit_db,
                    AuditEventInput(
                        actor_or_service_id="system_service",
                        role="system_service",
                        action="notification.dispatch",
                        affected_case_or_record=application_id,
                        outcome=notification.delivery_status,
                        reason=notification.failure_reason,
                        source="notification_service",
                        correlation_reference=correlation_reference,
                        metadata_reference=notification.notification_id,
                    ),
                )

    return NotificationDispatchResult(created=created, skipped_by_preference=tuple(skipped))
