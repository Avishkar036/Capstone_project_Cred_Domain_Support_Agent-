"""Retrieve knowledge-base chunks and produce grounded MOCK_LLM responses."""

from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

from rag_index import CHROMA_DIR, MODEL_NAME


IN_SCOPE_QUERIES = (
    "What documents are needed for KYC?",
    "How is EMI calculated?",
    "What happens when a customer reports a fraudulent transaction?",
    "What affects a credit score?",
    "Can an NRI open an account?",
)
OUT_OF_SCOPE_QUERIES = (
    "What is the weather forecast tomorrow?",
    "Who won yesterday's cricket match?",
)


def _collection_name(strategy: str) -> str:
    if strategy not in {"fixed", "sentence"}:
        raise ValueError("strategy must be 'fixed' or 'sentence'")
    return f"cred_{strategy}_chunks"


def retrieve(
    query: str,
    strategy: str = "sentence",
    top_k: int = 3,
    client: Any | None = None,
    model: SentenceTransformer | None = None,
) -> list[dict[str, Any]]:
    """Return top-k chunks with cosine similarity and source metadata."""
    client = client or chromadb.PersistentClient(path=str(CHROMA_DIR))
    model = model or SentenceTransformer(MODEL_NAME)
    collection = client.get_collection(_collection_name(strategy))
    result = collection.query(
        query_embeddings=model.encode([query], normalize_embeddings=True).tolist(),
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {"text": text, "metadata": metadata, "similarity": 1 - distance}
        for text, metadata, distance in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]


def calibrate_threshold(
    strategy: str = "sentence",
    in_scope: tuple[str, ...] = IN_SCOPE_QUERIES,
    out_of_scope: tuple[str, ...] = OUT_OF_SCOPE_QUERIES,
) -> tuple[float, list[float], list[float]]:
    """Choose a midpoint threshold between observed in/out top-1 similarities."""
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    in_scores = [retrieve(query, strategy, 1, client, model)[0]["similarity"] for query in in_scope]
    out_scores = [retrieve(query, strategy, 1, client, model)[0]["similarity"] for query in out_of_scope]
    threshold = (min(in_scores) + max(out_scores)) / 2
    return threshold, in_scores, out_scores


def grounded_answer(
    query: str,
    strategy: str = "sentence",
    threshold: float | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """Return an answer composed only from retrieved context or an explicit fallback."""
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if threshold is None:
        threshold, _, _ = calibrate_threshold(strategy)
    results = retrieve(query, strategy, top_k, client, model)
    if not results or results[0]["similarity"] < threshold:
        return {"answer": "I don't know based on the available policy documents.", "sources": [], "similarity": results[0]["similarity"] if results else 0.0}
    return {
        "answer": " ".join(item["text"] for item in results),
        "sources": [item["metadata"]["source"] for item in results],
        "similarity": results[0]["similarity"],
    }


if __name__ == "__main__":
    threshold, in_scores, out_scores = calibrate_threshold()
    print(f"In-scope top-1 similarities: {[round(score, 4) for score in in_scores]}")
    print(f"Out-of-scope top-1 similarities: {[round(score, 4) for score in out_scores]}")
    print(f"Calibrated fallback threshold: {threshold:.4f}")
    print(grounded_answer(IN_SCOPE_QUERIES[0], threshold=threshold))
    print(grounded_answer(OUT_OF_SCOPE_QUERIES[0], threshold=threshold))
