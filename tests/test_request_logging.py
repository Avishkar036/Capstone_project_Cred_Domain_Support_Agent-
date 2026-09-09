"""Tests for Task 12 structured logging."""

import json
import tempfile
import unittest
from pathlib import Path

from request_logging import write_request_log


class RequestLoggingTests(unittest.TestCase):
    def test_log_is_jsonl_and_masks_pii(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requests.jsonl"
            entry = write_request_log(
                "POST", "/ask", "PAN ABCDE1234F account 123456789012", 200, 0.0, path
            )
            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(stored, entry)
            self.assertRegex(entry["trace_id"], r"^[0-9a-f-]{36}$")
            self.assertNotIn("ABCDE1234F", entry["request_text"])
            self.assertNotIn("123456789012", entry["request_text"])
            self.assertGreaterEqual(entry["elapsed_ms"], 0)


if __name__ == "__main__":
    unittest.main()
