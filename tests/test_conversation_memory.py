"""Tests for Task 8 persisted and reset conversation memory."""

import json
import tempfile
import unittest
from pathlib import Path

from conversation_memory import ConversationMemory


class ConversationMemoryTests(unittest.TestCase):
    def test_multi_turn_history_persists_and_fresh_memory_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.json"
            memory = ConversationMemory(path)
            memory.add("user", "What is my loan status?")
            memory.add("assistant", "Your application is under review.")
            memory.add("user", "What should I do next?")

            reopened = ConversationMemory(path)
            self.assertEqual(len(reopened.context()), 3)
            self.assertEqual(reopened.context()[1]["content"], "Your application is under review.")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), reopened.context())

            reopened.reset()
            fresh = ConversationMemory(path)
            self.assertEqual(fresh.context(), [])

    def test_invalid_role_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                ConversationMemory(Path(directory) / "memory.json").add("system", "bad")


if __name__ == "__main__":
    unittest.main()
