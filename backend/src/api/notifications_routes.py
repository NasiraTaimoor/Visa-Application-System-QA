"""Notification preference and status timeline API routes (T151)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_identity
from src.applications.models.visa_application import VisaApplication
from src.applications.status.status_timeline_service import get_status_timeline
from src.auth.identity_provider import Identity
from src.db.session import get_db
from src.notifications.preference_service import set_preference

router = APIRouter(tags=["notifications"])


class NotificationPreferenceRequest(BaseModel):
    channel: str
    opted_out_events: list[str] = []


@router.post("/applications/{application_id}/notification-preferences")
def create_notification_preference_endpoint(
    application_id: str,
    payload: NotificationPreferenceRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
):
    application = db.get(VisaApplication, application_id)
    preference = set_preference(
        db, application.applicant_id, payload.channel, payload.opted_out_events
    )
    return {"channel": preference.channel, "opted_out_events": list(preference.opted_out_events)}


@router.get("/applications/{application_id}/status-timeline")
def get_status_timeline_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
):
    timeline = get_status_timeline(db, identity, application_id)
    return {
        "timeline": [
            {
                "new_status": e.new_status,
                "previous_status": e.previous_status,
                "timestamp": e.timestamp,
                "reason": e.reason,
                "next_action": e.next_action,
            }
            for e in timeline
        ]
    }
