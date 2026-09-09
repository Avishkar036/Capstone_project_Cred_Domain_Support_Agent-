"""Loan-application lookup tool for the Cred support agent."""

from typing import Any

from dataset import LOAN_APPLICATIONS


FRAUD_WEIGHT = 0.6
RECENCY_WEIGHT = 0.4
ESCALATION_THRESHOLD = 0.65


def check_loan_application_status(record_id: str) -> dict[str, Any]:
    """Return status, amount, and an escalation score for one application.

    The score is 0.6 when fraud review is flagged, plus 0.4 times the
    normalized age signal (days_since_created / 30). Applications at or above
    0.65 are recommended for escalation.
    """
    application = next(
        (item for item in LOAN_APPLICATIONS if item["record_id"] == record_id),
        None,
    )
    if application is None:
        raise KeyError(f"Unknown loan application record_id: {record_id}")
    recency_signal = application["days_since_created"] / 30
    escalation_score = round(
        FRAUD_WEIGHT * int(application["flagged_for_fraud_review"])
        + RECENCY_WEIGHT * recency_signal,
        4,
    )
    return {
        "record_id": record_id,
        "status": application["status"],
        "loan_amount_inr": application["loan_amount_inr"],
        "escalation_score": escalation_score,
        "recommend_escalation": escalation_score >= ESCALATION_THRESHOLD,
    }
