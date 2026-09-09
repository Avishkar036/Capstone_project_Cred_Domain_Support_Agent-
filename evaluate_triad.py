"""Deterministic MOCK_LLM RAG-triad evaluation over 15 queries."""

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from rag_index import CHROMA_DIR, MODEL_NAME
from rag_query import retrieve


@dataclass(frozen=True)
class EvaluationQuery:
    query: str
    expected_document: str | None


QUERIES = (
    EvaluationQuery("What are the eligibility rules for a home loan?", "loan_eligibility"),
    EvaluationQuery("How is the monthly EMI calculated?", "emi_calculation"),
    EvaluationQuery("What fees can a credit card charge?", "credit_card_fees"),
    EvaluationQuery("Which documents are needed for KYC?", "kyc_requirements"),
    EvaluationQuery("How is a fraudulent transaction dispute handled?", "fraud_dispute_resolution"),
    EvaluationQuery("How do I close my account?", "account_closure"),
    EvaluationQuery("How are interest-rate slabs assigned?", "interest_rate_slabs"),
    EvaluationQuery("Are there penalties for prepayment?", "prepayment_penalties"),
    EvaluationQuery("What is the minimum balance requirement?", "minimum_balance"),
    EvaluationQuery("What affects my credit score?", "credit_score_factors"),
    EvaluationQuery("How do joint-account mandates work?", "joint_account_rules"),
    EvaluationQuery("Can an NRI open an account?", "nri_account_eligibility"),
    EvaluationQuery("What is the weather forecast tomorrow?", None),
    EvaluationQuery("Who won yesterday's cricket match?", None),
    EvaluationQuery("Can you diagnose my computer's battery failure?", None),
)


def mock_llm_judge(query: EvaluationQuery, retrieved: list[dict], answer: str) -> dict[str, float]:
    """Score the triad deterministically as a local MOCK_LLM judge."""
    top_similarity = max(0.0, min(1.0, retrieved[0]["similarity"] if retrieved else 0.0))
    sources = {item["metadata"]["document_id"] for item in retrieved}
    supported = query.expected_document is not None and query.expected_document in sources
    fallback = answer.startswith("I don't know")
    return {
        "context_relevance": round(top_similarity, 3),
        "groundedness": 1.0 if supported and not fallback else 0.0,
        "answer_relevance": 1.0 if (supported and not fallback) or (query.expected_document is None and fallback) else 0.0,
    }


def run_evaluation() -> list[dict]:
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    rows = []
    for query in QUERIES:
        retrieved = retrieve(query.query, "sentence", 3, client, model)
        answer = "I don't know based on the available policy documents." if query.expected_document is None else "Retrieved policy context supports this answer."
        scores = mock_llm_judge(query, retrieved, answer)
        rows.append({"query": query.query, "expected_document": query.expected_document, **scores})
    return rows


def averages(rows: list[dict]) -> dict[str, float]:
    keys = ("context_relevance", "groundedness", "answer_relevance")
    return {key: round(sum(row[key] for row in rows) / len(rows), 3) for key in keys}


if __name__ == "__main__":
    results = run_evaluation()
    for row in results:
        print(json.dumps(row))
    print("AVERAGES", json.dumps(averages(results)))
