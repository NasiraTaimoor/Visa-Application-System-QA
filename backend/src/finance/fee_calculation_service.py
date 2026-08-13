"""Fee calculation service: visa type, agency relationship, stage, fee
version (T092)."""

from dataclasses import dataclass

from src.config import get_policy_config


class UnknownFeeError(ValueError):
    pass


@dataclass(frozen=True)
class FeeBreakdown:
    amount: int
    currency: str
    fee_version: str
    stage: str


def calculate_fees(visa_type: str, stage: str = "sub_agency_submission") -> FeeBreakdown:
    policy = get_policy_config()
    schedule = policy.fee_schedule.get(visa_type)
    if schedule is None or stage not in schedule:
        raise UnknownFeeError(f"no fee configured for visa type '{visa_type}' at stage '{stage}'")
    return FeeBreakdown(
        amount=schedule[stage],
        currency=policy.fee_currency,
        fee_version=policy.fee_schedule_version,
        stage=stage,
    )
