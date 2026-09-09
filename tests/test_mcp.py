"""Tests for Task 14 MCP tool registration and client configuration."""

import unittest

from mcp_client import lookup
from mcp_server import lookup_loan_application, mcp


class McpTests(unittest.TestCase):
    def test_server_tool_wrapper(self) -> None:
        result = lookup_loan_application("LA-0001")
        self.assertEqual(result["record_id"], "LA-0001")
        self.assertIn("escalation_score", result)

    def test_server_and_client_are_defined(self) -> None:
        self.assertIsNotNone(mcp)
        self.assertTrue(callable(lookup))


if __name__ == "__main__":
    unittest.main()
