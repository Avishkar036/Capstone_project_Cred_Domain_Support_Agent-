"""Validation tests for the Task 2 knowledge base."""

from pathlib import Path
import re
import unittest


KNOWLEDGE_BASE = Path(__file__).parents[1] / "knowledge_base"
REQUIRED_TOPICS = {
    "loan_eligibility.md",
    "emi_calculation.md",
    "credit_card_fees.md",
    "kyc_requirements.md",
    "fraud_dispute_resolution.md",
    "account_closure.md",
    "interest_rate_slabs.md",
    "prepayment_penalties.md",
    "minimum_balance.md",
    "credit_score_factors.md",
    "joint_account_rules.md",
    "nri_account_eligibility.md",
}


class KnowledgeBaseTests(unittest.TestCase):
    def test_all_required_documents_exist(self) -> None:
        self.assertEqual(
            REQUIRED_TOPICS,
            {path.name for path in KNOWLEDGE_BASE.glob("*.md")},
        )

    def test_each_document_has_two_to_five_sentences(self) -> None:
        for filename in REQUIRED_TOPICS:
            text = (KNOWLEDGE_BASE / filename).read_text(encoding="utf-8")
            body = text.split("\n\n", 1)[1]
            sentences = [part for part in re.split(r"(?<=[.!?])\s+", body.strip()) if part]
            self.assertGreaterEqual(len(sentences), 2, filename)
            self.assertLessEqual(len(sentences), 5, filename)


if __name__ == "__main__":
    unittest.main()
