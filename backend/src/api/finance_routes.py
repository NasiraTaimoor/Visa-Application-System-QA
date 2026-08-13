"""Finance API routes: fees, wallet verification, sub-agency submission (T096)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_correlation_reference, get_identity
from src.applications.submission.sub_agency_submission_service import submit_to_main_agency
from src.auth.identity_provider import Identity
from src.db.session import get_db
from src.finance.fee_calculation_service import calculate_fees
from src.finance.wallet_lifecycle_service import verify_and_reserve

router = APIRouter(tags=["finance"])


@router.get("/applications/{application_id}/fees")
def calculate_fees_endpoint(application_id: str, db: Session = Depends(get_db)):
    from src.applications.models.visa_application import VisaApplication

    application = db.get(VisaApplication, application_id)
    fee = calculate_fees(application.visa_type)
    return {
        "amount": fee.amount,
        "currency": fee.currency,
        "fee_version": fee.fee_version,
        "stage": fee.stage,
    }


@router.post("/applications/{application_id}/wallet/verify")
def verify_wallet_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    outcome = verify_and_reserve(db, identity, application_id, correlation_reference)
    return {
        "sufficient": outcome.sufficient,
        "amount": outcome.amount,
        "currency": outcome.currency,
        "fee_version": outcome.fee_version,
        "available_balance_result": outcome.available_balance_result,
        "reservation_reference": outcome.reservation_reference,
        "shortfall_amount": outcome.shortfall_amount,
    }


@router.post("/applications/{application_id}/submit")
def submit_to_main_agency_endpoint(
    application_id: str,
    db: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
    correlation_reference: str = Depends(get_correlation_reference),
):
    result = submit_to_main_agency(db, identity, application_id, correlation_reference)
    return {
        "submission_reference": result.submission_reference,
        "snapshot_id": result.snapshot_id,
        "current_status": result.current_status,
    }
