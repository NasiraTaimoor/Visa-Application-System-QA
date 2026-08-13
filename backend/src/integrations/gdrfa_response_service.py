"""GDRFA response handling service: ack/reject/action-required/timeout/
duplicate/unavailable outcomes, source validation, quarantine (T113).

Submission and response handling are combined into one synchronous flow here
since the mocked adapter (T112) responds immediately; a real deployment
would split "submit" (async request) from "handle webhook/poll response"
across a queue, but the state effects are identical.
"""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.agencies.models.processing_task import ProcessingTask
from src.applications.idempotency.idempotency_store import DuplicateRequestReplay, claim_or_replay
from src.applications.models.applicant import Applicant
from src.applications.models.status_event import StatusEvent
from src.applications.models.submission import Submission
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.integrations.gdrfa_adapter import submit_to_gdrfa
from src.integrations.models.external_case_response import ExternalCaseResponse


class ApplicationNotFoundError(ValueError):
    pass


class ReadinessNotApprovedError(ValueError):
    pass


class InvalidGdrfaStateError(ValueError):
    pass


@dataclass(frozen=True)
class GdrfaSubmissionOutcome:
    submission_reference: str
    response_type: str
    current_status: str
    response_reason: str | None


def submit_and_handle_response(
    db: Session, identity: Identity, application_id: str, correlation_reference: str
) -> GdrfaSubmissionOutcome:
    application = db.get(VisaApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="gdrfa:submit",
            owning_agency_id=application.routed_main_agency_id,
        )
    )

    idempotency_key = f"gdrfa_submit:{application_id}"
    try:
        claim_or_replay(db, idempotency_key, scope="gdrfa_submit", result_reference=application_id)
    except DuplicateRequestReplay:
        existing = db.query(Submission).filter_by(idempotency_key=idempotency_key).one_or_none()
        if existing is not None:
            response = (
                db.query(ExternalCaseResponse)
                .filter_by(application_id=application_id, source_system="gdrfa")
                .order_by(ExternalCaseResponse.received_at.desc())
                .first()
            )
            return GdrfaSubmissionOutcome(
                submission_reference=existing.submission_reference,
                response_type=response.response_type if response else "unknown",
                current_status=application.current_status,
                response_reason=response.reason if response else None,
            )
        raise

    if application.current_status != "main_agency_processing":
        raise InvalidGdrfaStateError(
            "GDRFA submission requires status 'main_agency_processing', "
            f"case is '{application.current_status}'"
        )
    if application.readiness_approved_at is None:
        raise ReadinessNotApprovedError("readiness must be approved before GDRFA submission")

    applicant = db.get(Applicant, application.applicant_id)
    routing_signal = (
        f"{application.validated_snapshot_id or application_id} {applicant.legal_name or ''}"
    )
    result = submit_to_gdrfa(routing_signal)
    submission_reference = f"GDRFA-SUB-{uuid.uuid4().hex[:12].upper()}"

    db.add(
        Submission(
            application_id=application_id,
            submission_type="gdrfa",
            source_agency_id=application.routed_main_agency_id or "main-agency-root",
            target_agency_or_system="gdrfa",
            snapshot_id=application.validated_snapshot_id or application_id,
            submission_reference=submission_reference,
            external_reference=result.external_reference,
            status="submitted",
            idempotency_key=idempotency_key,
        )
    )
    db.add(
        ExternalCaseResponse(
            application_id=application_id,
            source_system="gdrfa",
            external_reference=result.external_reference or result.payload_reference,
            response_type=result.response_type,
            reason=result.response_reason,
            payload_reference=result.payload_reference,
            matched_status="matched",
            idempotency_key=f"gdrfa_response:{application_id}:{result.payload_reference}",
        )
    )

    # First transition always occurs: the submission attempt itself.
    step = transition(application.current_status, "gdrfa_submitted")
    application.current_status = step.new_status
    db.add(
        StatusEvent(
            application_id=application_id,
            previous_status=step.previous_status,
            new_status=step.new_status,
            source="gdrfa_service",
            actor_or_service_id=identity.user_id,
            responsible_party="gdrfa_immigration_liaison",
            external_reference=result.external_reference,
            reason=result.response_reason,
            correlation_reference=correlation_reference,
        )
    )

    if result.response_type == "acknowledged":
        step2 = transition(application.current_status, "payment_pending")
        application.current_status = step2.new_status
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=step2.previous_status,
                new_status=step2.new_status,
                source="gdrfa_service",
                actor_or_service_id=identity.user_id,
                responsible_party="finance_officer",
                next_action="Initiate or confirm payment",
                correlation_reference=correlation_reference,
            )
        )
    elif result.response_type == "rejected":
        step2 = transition(application.current_status, "correction_requested")
        application.current_status = step2.new_status
        db.add(
            StatusEvent(
                application_id=application_id,
                previous_status=step2.previous_status,
                new_status=step2.new_status,
                source="gdrfa_service",
                actor_or_service_id=identity.user_id,
                responsible_party="main_agency_case_officer",
                reason=result.response_reason,
                next_action="Correct the identified issue and resubmit",
                correlation_reference=correlation_reference,
            )
        )
    elif result.response_type in ("timeout", "action_required"):
        db.add(
            ProcessingTask(
                application_id=application_id,
                task_type=f"gdrfa_{result.response_type}",
                assigned_role="gdrfa_immigration_liaison",
                owning_agency_id=application.routed_main_agency_id or "main-agency-root",
                status="open",
                reason=result.response_reason or result.response_type,
            )
        )

    db.commit()
    db.refresh(application)

    with AuditSessionLocal() as audit_db:
        record_audit_event(
            audit_db,
            AuditEventInput(
                actor_or_service_id=identity.user_id,
                role=identity.role,
                agency_scope=application.routed_main_agency_id,
                action="gdrfa.submit",
                affected_case_or_record=application_id,
                outcome=result.response_type,
                reason=result.response_reason,
                source="gdrfa_service",
                correlation_reference=correlation_reference,
                metadata_reference=submission_reference,
            ),
        )

    from src.notifications.notification_rules_engine import trigger_notification

    trigger_notification(db, application_id, "gdrfa_response", correlation_reference)

    return GdrfaSubmissionOutcome(
        submission_reference=submission_reference,
        response_type=result.response_type,
        current_status=application.current_status,
        response_reason=result.response_reason,
    )
