"""Deterministic sample loan-application data for the Cred support agent."""

from collections import Counter
import random
from typing import Any


SEED = 20260909
RECORD_COUNT = 50
MIN_LOAN_AMOUNT_INR = 25_000
MAX_LOAN_AMOUNT_INR = 2_500_000

CATEGORIES = (
    "Personal Loan",
    "Home Loan",
    "Auto Loan",
    "Education Loan",
    "Business Loan",
)

STATUSES = (
    "Submitted",
    "Under Review",
    "Approved",
    "Rejected",
    "Disbursed",
)

# The pools make coverage explicit; seeded shuffling determines each record's values.
CATEGORY_POOL = tuple(category for category in CATEGORIES for _ in range(10))
STATUS_POOL = (
    ("Submitted",) * 10
    + ("Under Review",) * 12
    + ("Approved",) * 12
    + ("Rejected",) * 8
    + ("Disbursed",) * 8
)
FRAUD_REVIEW_POOL = (True,) * 10 + (False,) * 40


def generate_loan_applications() -> list[dict[str, Any]]:
    """Return 50 seeded loan applications with the required field constraints."""
    rng = random.Random(SEED)
    categories = list(CATEGORY_POOL)
    statuses = list(STATUS_POOL)
    fraud_flags = list(FRAUD_REVIEW_POOL)
    rng.shuffle(categories)
    rng.shuffle(statuses)
    rng.shuffle(fraud_flags)

    return [
        {
            "record_id": f"LA-{index:04d}",
            "category": categories[index - 1],
            "status": statuses[index - 1],
            "loan_amount_inr": rng.randint(
                MIN_LOAN_AMOUNT_INR, MAX_LOAN_AMOUNT_INR
            ),
            "days_since_created": rng.randint(0, 30),
            "flagged_for_fraud_review": fraud_flags[index - 1],
        }
        for index in range(1, RECORD_COUNT + 1)
    ]


LOAN_APPLICATIONS = generate_loan_applications()


def dataset_summary(
    applications: list[dict[str, Any]] = LOAN_APPLICATIONS,
) -> tuple[Counter[str], Counter[str], float]:
    """Return category counts, status counts, and the fraud-review percentage."""
    category_counts = Counter(application["category"] for application in applications)
    status_counts = Counter(application["status"] for application in applications)
    fraud_review_percentage = (
        sum(application["flagged_for_fraud_review"] for application in applications)
        / len(applications)
        * 100
    )
    return category_counts, status_counts, fraud_review_percentage


if __name__ == "__main__":
    categories, statuses, fraud_percentage = dataset_summary()
    print("Loan amount range: INR 25,000 to INR 25,00,000, covering common unsecured and secured loan requests.")
    print(f"Category counts: {dict(categories)}")
    print(f"Status counts: {dict(statuses)}")
    print(f"Fraud-review percentage: {fraud_percentage:.1f}%")
