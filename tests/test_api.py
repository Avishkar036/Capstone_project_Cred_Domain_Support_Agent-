"""Tests for Task 11 FastAPI endpoints."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("api.AGENT.invoke", return_value={"response": {"route": "status", "answer": "Approved", "details": {}}})
    def test_ask_endpoint(self, invoke) -> None:
        response = self.client.post("/ask", json={"query": "Check LA-0001 status"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["route"], "status")
        invoke.assert_called_once()

    def test_add_document_endpoint_rejects_invalid_filename(self) -> None:
        response = self.client.post("/add-document", json={"filename": "bad.txt", "content": "text"})
        self.assertEqual(response.status_code, 422)

    def test_openapi_contains_required_endpoints(self) -> None:
        schema = self.client.get("/openapi.json").json()
        self.assertIn("/ask", schema["paths"])
        self.assertIn("/add-document", schema["paths"])


if __name__ == "__main__":
    unittest.main()
