"""Tests for Task 5 evaluation definitions."""

import unittest

from evaluate_rag import IN_SCOPE_QUERIES, RELEVANT_DOCUMENTS, mean


class RagEvaluationTests(unittest.TestCase):
    def test_five_queries_have_relevant_documents(self) -> None:
        self.assertEqual(len(IN_SCOPE_QUERIES), 5)
        self.assertEqual(set(IN_SCOPE_QUERIES), set(RELEVANT_DOCUMENTS))
        self.assertTrue(all(RELEVANT_DOCUMENTS[query] for query in IN_SCOPE_QUERIES))

    def test_mean(self) -> None:
        self.assertAlmostEqual(mean([0.0, 0.5, 1.0]), 0.5)


if __name__ == "__main__":
    unittest.main()
