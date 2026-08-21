"""Payment, reconciliation, and immigration-update API routes (T136)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.agencies.immigration_status_service import record_immigration_update
from src.api.deps import get_correlation_reference, get_identity
from src.auth.identity_provider import Identity
from src.db.session import get_db
from src.finance.payment_service import confirm_payment_event
from src.finance.reconciliation_service import ManualReconciliationCommand, reconcile_payment

router = APIRouter(tags=["payment-immigration"])


class ManualReconciliationRequest(BaseModel):
    receipt_reference: str
    amount: int
    currency: str
    reason: str


@router.post("/applications/{application_id}/payment/confirm")
def confirm_payment_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    outcome = confirm_payment_event(db, identity, application_id, correlation_reference)
    return {
        "payment_state": outcome.payment_state,
        "current_status": outcome.current_status,
        "reason": outcome.reason,
    }


@router.post("/applications/{application_id}/payment/reconcile")
def reconcile_payment_endpoint(
    application_id: str,
    payload: ManualReconciliationRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    application = reconcile_payment(
        db,
        identity,
        ManualReconciliationCommand(
            application_id=application_id,
            receipt_reference=payload.receipt_reference,
            amount=payload.amount,
            currency=payload.currency,
            reason=payload.reason,
            correlation_reference=correlation_reference,
        ),
    )
    return {
        "application_id": application.application_id,
        "current_status": application.current_status,
    }


@router.post("/applications/{application_id}/immigration/update")
def record_immigration_update_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    outcome = record_immigration_update(db, identity, application_id, correlation_reference)
    return {
        "response_type": outcome.response_type,
        "current_status": outcome.current_status,
        "quarantined": outcome.quarantined,
        "reason": outcome.reason,
    }
