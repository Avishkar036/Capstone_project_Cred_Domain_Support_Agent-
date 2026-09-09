"""Tests for the Task 6 loan-status tool."""

import unittest

from dataset import LOAN_APPLICATIONS
from loan_tools import ESCALATION_THRESHOLD, FRAUD_WEIGHT, RECENCY_WEIGHT, check_loan_application_status


class LoanToolsTests(unittest.TestCase):
    def test_lookup_returns_expected_fields_and_formula(self) -> None:
        application = LOAN_APPLICATIONS[0]
        result = check_loan_application_status(application["record_id"])
        expected_score = round(
            FRAUD_WEIGHT * int(application["flagged_for_fraud_review"])
            + RECENCY_WEIGHT * application["days_since_created"] / 30,
            4,
        )
        self.assertEqual(result["status"], application["status"])
        self.assertEqual(result["loan_amount_inr"], application["loan_amount_inr"])
        self.assertEqual(result["escalation_score"], expected_score)
        self.assertEqual(result["recommend_escalation"], expected_score >= ESCALATION_THRESHOLD)

    def test_unknown_record_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            check_loan_application_status("LA-9999")


if __name__ == "__main__":
    unittest.main()
