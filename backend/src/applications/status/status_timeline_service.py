"""Role-filtered status timeline query service (T150)."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity

_STATUS_READ_ACTIONS = {
    "applicant": "status:read_own",
    "sub_agency_officer": "status:read_own_agency",
    "sub_agency_admin": "status:read_own_agency",
    "main_agency_case_officer": "status:read_routed",
    "main_agency_supervisor": "status:read_routed",
    "gdrfa_immigration_liaison": "status:read_routed",
    "finance_officer": "status:read_financial",
}


class ApplicationNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class TimelineEntry:
    new_status: str
    previous_status: str | None
    timestamp: str
    reason: str | None
    next_action: str | None


def get_status_timeline(
    db: Session, identity: Identity, application_id: str
) -> list[TimelineEntry]:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    action = _STATUS_READ_ACTIONS.get(identity.role, "audit:read")
    scope = (
        application.owning_sub_agency_id
        if identity.role in ("sub_agency_officer", "sub_agency_admin")
        else (
            application.routed_main_agency_id
            if identity.role
            in ("main_agency_case_officer", "main_agency_supervisor", "gdrfa_immigration_liaison")
            else None
        )
    )
    # Note: applicant identity is not currently tied back to a specific
    # Applicant row anywhere in this scaffold (create_application does not
    # record which identity created the applicant), so applicant-level
    # ownership is not enforced here either, consistent with the rest of the
    # applicant-facing endpoints (resume_draft, update_intake).
    authorize(AuthorizationContext(identity=identity, action=action, owning_agency_id=scope))

    events = (
        db.query(StatusEvent)
        .filter_by(application_id=application_id)
        .order_by(StatusEvent.timestamp.asc())
        .all()
    )
    return [
        TimelineEntry(
            new_status=e.new_status,
            previous_status=e.previous_status,
            timestamp=e.timestamp.isoformat(),
            reason=e.reason,
            next_action=e.next_action,
        )
        for e in events
    ]
