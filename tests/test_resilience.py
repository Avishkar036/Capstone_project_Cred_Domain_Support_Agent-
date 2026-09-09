"""Tests for Task 16 timeout and retry behavior."""

import asyncio
import unittest

from resilience import global_timeout_demo, node_timeout_demo, transient_demo


class ResilienceTests(unittest.TestCase):
    def test_retry_recovers_after_two_failures(self) -> None:
        result, attempts = asyncio.run(transient_demo())
        self.assertEqual(result, "recovered")
        self.assertEqual(attempts, 3)

    def test_node_timeout_fires(self) -> None:
        with self.assertRaises(asyncio.TimeoutError):
            asyncio.run(node_timeout_demo())

    def test_global_timeout_fires(self) -> None:
        with self.assertRaises(asyncio.TimeoutError):
            asyncio.run(global_timeout_demo())


if __name__ == "__main__":
    unittest.main()
