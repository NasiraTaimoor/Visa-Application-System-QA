"""Finance-approved manual reconciliation service (T132).

Covers the "approved manual reconciliation" path in BR-023/E-007: when
automated provider confirmation is disputed, unmatched, or otherwise
unavailable, a finance officer can record a reconciled outcome with receipt,
amount, currency, and reason.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.applications.models.status_event import StatusEvent
from src.applications.models.visa_application import VisaApplication
from src.applications.workflow.state_machine import transition
from src.audit.audit_middleware import AuditEventInput, record_audit_event
from src.audit.store.base import AuditSessionLocal
from src.auth.authorization_policy import AuthorizationContext, authorize
from src.auth.identity_provider import Identity
from src.finance.models.payment import Payment
from src.finance.payment_service import _debit_reservation


class ApplicationNotFoundError(ValueError):
    pass


class InvalidReconciliationStateError(ValueError):
    pass


class ReasonRequiredError(ValueError):
    pass


@dataclass(frozen=True)
class ManualReconciliationCommand:
    application_id: str
    receipt_reference: str
    amount: int
    currency: str
    reason: str
    correlation_reference: str


def reconcile_payment(
    db: Session, identity: Identity, cmd: ManualReconciliationCommand
) -> VisaApplication:
    if not cmd.reason:
        raise ReasonRequiredError("a reconciliation reason is required")

    application = db.get(VisaApplication, cmd.application_id)
    if application is None:
        raise ApplicationNotFoundError(cmd.application_id)

    authorize(
        AuthorizationContext(
            identity=identity,
            action="payment:reconcile",
            business_reason=cmd.reason,
            requires_reason=True,
        )
    )

    if application.current_status not in ("payment_pending", "payment_failed"):
        raise InvalidReconciliationStateError(
            "reconciliation requires status 'payment_pending' or 'payment_failed', "
            f"case is '{application.current_status}'"
        )

    db.add(
        Payment(
            application_id=cmd.application_id,
            payment_state="reconciled",
            amount=cmd.amount,
            currency=cmd.currency,
            fee_version=application.fee_version or "unknown",
            receipt_reference=cmd.receipt_reference,
            confirmation_source="finance_manual_reconciliation",
            finance_actor_id=identity.user_id,
            reconciliation_status="reconciled",
            reason=cmd.reason,
            idempotency_key=f"payment_reconcile:{cmd.application_id}:{cmd.receipt_reference}",
        )
    )
    _debit_reservation(db, application)

    if application.current_status == "payment_failed":
        retry_step = transition(application.current_status, "payment_pending")
        application.current_status = retry_step.new_status
    step = transition(application.current_status, "paid")
    application.current_status = step.new_status
    db.add(
        StatusEvent(
            application_id=cmd.application_id,
            previous_status=step.previous_status,
            new_status=step.new_status,
            source="finance_api",
            actor_or_service_id=identity.user_id,
            responsible_party="gdrfa_immigration_liaison",
            reason=cmd.reason,
            next_action="Await immigration processing handoff",
            correlation_reference=cmd.correlation_reference,
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
                agency_scope=application.owning_sub_agency_id,
                action="payment.manual_reconciliation",
                affected_case_or_record=cmd.application_id,
                outcome="reconciled",
                reason=cmd.reason,
                source="finance_api",
                correlation_reference=cmd.correlation_reference,
            ),
        )

    from src.notifications.notification_rules_engine import trigger_notification

    trigger_notification(db, cmd.application_id, "payment_outcome", cmd.correlation_reference)

    return application
