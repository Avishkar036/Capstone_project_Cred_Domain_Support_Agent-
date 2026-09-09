"""Tests for Task 4 retrieval and grounded fallback behavior."""

import unittest

from rag_query import _collection_name


class RagQueryTests(unittest.TestCase):
    def test_collection_names(self) -> None:
        self.assertEqual(_collection_name("fixed"), "cred_fixed_chunks")
        self.assertEqual(_collection_name("sentence"), "cred_sentence_chunks")

    def test_invalid_strategy_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _collection_name("unknown")


if __name__ == "__main__":
    unittest.main()
