"""LangGraph orchestration for policy questions and loan-status queries."""

import re
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from loan_tools import check_loan_application_status
from rag_query import grounded_answer
from response_schema import validate_response
from guardrails import check_grounded_output, guard_input


class AgentState(TypedDict, total=False):
    query: str
    route: str
    result: dict[str, Any]
    response: dict[str, Any]


def classify_query(state: AgentState) -> AgentState:
    """Classify record-ID requests as status queries and all others as policy."""
    query = guard_input(state["query"])
    state["query"] = query
    state["route"] = "status" if re.search(r"\bLA-\d{4}\b", query, re.IGNORECASE) else "rag"
    return state


def route_query(state: AgentState) -> str:
    """Choose the conditional graph edge after classification."""
    return state["route"]


def answer_with_rag(state: AgentState) -> AgentState:
    state["result"] = check_grounded_output(grounded_answer(state["query"]))
    return state


def answer_with_status(state: AgentState) -> AgentState:
    match = re.search(r"\b(LA-\d{4})\b", state["query"], re.IGNORECASE)
    if not match:
        raise ValueError("A status route requires a loan record ID")
    state["result"] = check_loan_application_status(match.group(1).upper())
    return state


def format_response(state: AgentState) -> AgentState:
    result = state["result"]
    if state["route"] == "status":
        answer = (
            f"Application {result['record_id']} is {result['status']}. "
            f"Loan amount: INR {result['loan_amount_inr']}. "
            f"Escalation score: {result['escalation_score']:.4f}."
        )
    else:
        answer = result["answer"]
    state["response"] = validate_response(
        {"route": state["route"], "answer": answer, "details": result}
    )
    return state


def build_agent():
    """Build and compile the four-node conditional LangGraph agent."""
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_query)
    graph.add_node("rag", answer_with_rag)
    graph.add_node("status", answer_with_status)
    graph.add_node("format", format_response)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_query, {"rag": "rag", "status": "status"})
    graph.add_edge("rag", "format")
    graph.add_edge("status", "format")
    graph.add_edge("format", END)
    return graph.compile()


if __name__ == "__main__":
    graph = build_agent().get_graph()
    print("Nodes:", sorted(graph.nodes))
    print("Edges:", [(edge.source, edge.target) for edge in graph.edges])
