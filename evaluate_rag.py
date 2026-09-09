"""Compare document-level Precision@3 and Recall@3 for both chunking strategies."""

from collections.abc import Iterable

import chromadb
from sentence_transformers import SentenceTransformer

from rag_index import CHROMA_DIR, MODEL_NAME
from rag_query import IN_SCOPE_QUERIES, retrieve


RELEVANT_DOCUMENTS = {
    IN_SCOPE_QUERIES[0]: {"kyc_requirements"},
    IN_SCOPE_QUERIES[1]: {"emi_calculation"},
    IN_SCOPE_QUERIES[2]: {"fraud_dispute_resolution"},
    IN_SCOPE_QUERIES[3]: {"credit_score_factors"},
    IN_SCOPE_QUERIES[4]: {"nri_account_eligibility"},
}


def evaluate_query(query: str, strategy: str, model, client) -> dict[str, object]:
    """Calculate document-level precision and recall for one query."""
    retrieved = retrieve(query, strategy, 3, client, model)
    predicted = {item["metadata"]["document_id"] for item in retrieved}
    relevant = RELEVANT_DOCUMENTS[query]
    hits = predicted & relevant
    return {
        "query": query,
        "retrieved": sorted(predicted),
        "relevant": sorted(relevant),
        "hits": sorted(hits),
        "precision": len(hits) / 3,
        "recall": len(hits) / len(relevant),
    }


def evaluate_strategy(strategy: str, model, client) -> list[dict[str, object]]:
    return [evaluate_query(query, strategy, model, client) for query in IN_SCOPE_QUERIES]


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values)


if __name__ == "__main__":
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    for strategy in ("fixed", "sentence"):
        results = evaluate_strategy(strategy, model, client)
        print(f"\n{strategy.title()} strategy")
        for result in results:
            print(
                f"{result['query']} | retrieved={result['retrieved']} | "
                f"relevant={result['relevant']} | hits={result['hits']} | "
                f"Precision@3={result['precision']:.3f} | Recall@3={result['recall']:.3f}"
            )
        print(f"Mean Precision@3: {mean(r['precision'] for r in results):.3f}")
        print(f"Mean Recall@3: {mean(r['recall'] for r in results):.3f}")
