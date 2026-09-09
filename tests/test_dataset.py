"""Tests for the Task 1 deterministic loan-application dataset."""

import unittest

from dataset import (
    CATEGORIES,
    MAX_LOAN_AMOUNT_INR,
    MIN_LOAN_AMOUNT_INR,
    RECORD_COUNT,
    STATUSES,
    dataset_summary,
    generate_loan_applications,
)


class LoanApplicationDatasetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.applications = generate_loan_applications()

    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(self.applications, generate_loan_applications())

    def test_record_count_ids_and_fields(self) -> None:
        self.assertEqual(RECORD_COUNT, 50)
        self.assertEqual(len(self.applications), RECORD_COUNT)
        self.assertEqual(
            [application["record_id"] for application in self.applications],
            [f"LA-{index:04d}" for index in range(1, RECORD_COUNT + 1)],
        )
        required_fields = {
            "record_id",
            "category",
            "status",
            "loan_amount_inr",
            "days_since_created",
            "flagged_for_fraud_review",
        }
        for application in self.applications:
            self.assertEqual(set(application), required_fields)

    def test_categories_and_statuses_have_required_coverage(self) -> None:
        category_counts, status_counts, _ = dataset_summary(self.applications)
        self.assertEqual(set(category_counts), set(CATEGORIES))
        self.assertEqual(set(status_counts), set(STATUSES))
        self.assertTrue(all(category_counts[category] >= 3 for category in CATEGORIES))
        self.assertTrue(all(status_counts[status] >= 1 for status in STATUSES))

    def test_numeric_ranges_and_fraud_review_rate(self) -> None:
        _, _, fraud_review_percentage = dataset_summary(self.applications)
        for application in self.applications:
            self.assertGreaterEqual(application["loan_amount_inr"], MIN_LOAN_AMOUNT_INR)
            self.assertLessEqual(application["loan_amount_inr"], MAX_LOAN_AMOUNT_INR)
            self.assertGreaterEqual(application["days_since_created"], 0)
            self.assertLessEqual(application["days_since_created"], 30)
            self.assertIsInstance(application["flagged_for_fraud_review"], bool)
        self.assertGreaterEqual(fraud_review_percentage, 10)
        self.assertLessEqual(fraud_review_percentage, 30)


if __name__ == "__main__":
    unittest.main()
