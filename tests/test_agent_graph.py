"""Tests for Task 7 graph structure and conditional routing."""

import unittest

from agent_graph import build_agent, classify_query, route_query


class AgentGraphTests(unittest.TestCase):
    def test_routes_status_and_policy_intents(self) -> None:
        self.assertEqual(route_query(classify_query({"query": "Check LA-0001 status"})), "status")
        self.assertEqual(route_query(classify_query({"query": "What KYC documents are needed?"})), "rag")

    def test_graph_has_four_nodes_and_conditional_paths(self) -> None:
        graph = build_agent().get_graph()
        node_names = set(graph.nodes)
        self.assertTrue({"classify", "rag", "status", "format"}.issubset(node_names))
        self.assertGreaterEqual(len(node_names), 4)
        edges = {(edge.source, edge.target) for edge in graph.edges}
        self.assertIn(("classify", "rag"), edges)
        self.assertIn(("classify", "status"), edges)


if __name__ == "__main__":
    unittest.main()
