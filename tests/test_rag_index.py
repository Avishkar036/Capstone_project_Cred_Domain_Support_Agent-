"""Unit tests for Task 3 chunking and document metadata."""

import unittest

from rag_index import build_chunks, fixed_size_chunks, load_documents, sentence_chunks


class RagIndexTests(unittest.TestCase):
    def test_loads_all_knowledge_base_documents(self) -> None:
        self.assertEqual(len(load_documents()), 12)

    def test_fixed_chunks_overlap_and_sentence_chunks(self) -> None:
        text = "One two three four five six seven eight nine ten eleven twelve. Next sentence is here."
        fixed = fixed_size_chunks(text, size=35, overlap=10)
        sentences = sentence_chunks(text)
        self.assertGreater(len(fixed), 1)
        self.assertEqual(len(sentences), 2)
        self.assertIn("Next sentence is here.", sentences)

    def test_chunk_records_keep_parent_document_metadata(self) -> None:
        records = build_chunks(load_documents()[:1], "sentence")
        self.assertTrue(records)
        self.assertTrue(all(record["metadata"]["document_id"] == "account_closure" for record in records))
        self.assertTrue(all(record["metadata"]["strategy"] == "sentence" for record in records))

    def test_invalid_fixed_chunk_parameters_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fixed_size_chunks("text", size=10, overlap=10)


if __name__ == "__main__":
    unittest.main()
