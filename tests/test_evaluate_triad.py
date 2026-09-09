"""Tests for Task 13 RAG-triad evaluation definitions."""

import unittest

from evaluate_triad import MOCK_LLM_JUDGE_PROMPT, QUERIES, averages, mock_llm_judge


class TriadEvaluationTests(unittest.TestCase):
    def test_fifteen_queries_cover_topics_and_edge_cases(self) -> None:
        self.assertEqual(len(QUERIES), 15)
        self.assertEqual(sum(query.expected_document is None for query in QUERIES), 3)
        self.assertEqual(len({query.expected_document for query in QUERIES if query.expected_document}), 12)

    def test_mock_judge_scores_supported_and_out_of_scope(self) -> None:
        supported = mock_llm_judge(QUERIES[0], [{"similarity": 0.8, "metadata": {"document_id": "loan_eligibility"}}], "supported")
        out_of_scope = mock_llm_judge(QUERIES[-1], [{"similarity": 0.1, "metadata": {"document_id": "kyc_requirements"}}], "I don't know based on the available policy documents.")
        self.assertEqual(supported["groundedness"], 1.0)
        self.assertEqual(out_of_scope["answer_relevance"], 1.0)

    def test_averages(self) -> None:
        rows = [{"context_relevance": 0.5, "groundedness": 1.0, "answer_relevance": 0.0}]
        self.assertEqual(averages(rows), {"context_relevance": 0.5, "groundedness": 1.0, "answer_relevance": 0.0})

    def test_mock_llm_prompt_is_declared(self) -> None:
        self.assertIn("MOCK_LLM", MOCK_LLM_JUDGE_PROMPT)
        self.assertIn("context_relevance", MOCK_LLM_JUDGE_PROMPT)
        self.assertIn("groundedness", MOCK_LLM_JUDGE_PROMPT)
        self.assertIn("answer_relevance", MOCK_LLM_JUDGE_PROMPT)


if __name__ == "__main__":
    unittest.main()
