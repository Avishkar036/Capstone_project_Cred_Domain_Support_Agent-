"""Tests for Task 9 structured response validation."""

import unittest

from response_schema import validate_response


class ResponseSchemaTests(unittest.TestCase):
    def test_valid_response(self) -> None:
        response = {"route": "status", "answer": "Approved", "details": {"status": "Approved"}}
        self.assertIs(validate_response(response), response)

    def test_missing_field_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_response({"route": "rag", "answer": "Answer"})

    def test_invalid_route_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_response({"route": "other", "answer": "Answer", "details": {}})


if __name__ == "__main__":
    unittest.main()
