"""Chunk, embed, and index the Cred knowledge base in two Chroma collections."""

from pathlib import Path
import re
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"
CHROMA_DIR = Path(__file__).parent / "chroma_db"
MODEL_NAME = "all-MiniLM-L6-v2"
FIXED_CHUNK_SIZE = 240
FIXED_CHUNK_OVERLAP = 40


def load_documents(directory: Path = KNOWLEDGE_BASE_DIR) -> list[dict[str, str]]:
    """Load Markdown documents with stable IDs and source metadata."""
    return [
        {"document_id": path.stem, "source": path.name, "text": path.read_text(encoding="utf-8")}
        for path in sorted(directory.glob("*.md"))
    ]


def fixed_size_chunks(
    text: str,
    size: int = FIXED_CHUNK_SIZE,
    overlap: int = FIXED_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into character chunks with a fixed overlap."""
    if size <= overlap:
        raise ValueError("size must be greater than overlap")
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        current: list[str] = []
        length = 0
        index = start
        while index < len(words) and (not current or length + len(words[index]) + 1 <= size):
            current.append(words[index])
            length += len(words[index]) + (1 if current else 0)
            index += 1
        chunks.append(" ".join(current))
        if index == len(words):
            break
        retained = 0
        next_start = index
        while next_start > start and retained < overlap:
            next_start -= 1
            retained += len(words[next_start]) + 1
        start = next_start
    return chunks


def sentence_chunks(text: str) -> list[str]:
    """Split text into sentence-based chunks, preserving short headings."""
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    return sentences


def build_chunks(documents: list[dict[str, str]], strategy: str) -> list[dict[str, Any]]:
    """Return chunk records with parent-document metadata."""
    chunker = fixed_size_chunks if strategy == "fixed" else sentence_chunks
    if strategy not in {"fixed", "sentence"}:
        raise ValueError("strategy must be 'fixed' or 'sentence'")
    records = []
    for document in documents:
        for position, text in enumerate(chunker(document["text"])):
            records.append(
                {
                    "id": f"{strategy}-{document['document_id']}-{position}",
                    "text": text,
                    "metadata": {
                        "document_id": document["document_id"],
                        "source": document["source"],
                        "chunk_index": position,
                        "strategy": strategy,
                    },
                }
            )
    return records


def index_strategy(
    client: chromadb.PersistentClient,
    model: SentenceTransformer,
    documents: list[dict[str, str]],
    strategy: str,
) -> int:
    """Embed and replace one strategy's Chroma collection."""
    collection = client.get_or_create_collection(f"cred_{strategy}_chunks", metadata={"hnsw:space": "cosine"})
    records = build_chunks(documents, strategy)
    if records:
        collection.upsert(
            ids=[record["id"] for record in records],
            documents=[record["text"] for record in records],
            embeddings=model.encode([record["text"] for record in records], normalize_embeddings=True).tolist(),
            metadatas=[record["metadata"] for record in records],
        )
    return len(records)


def build_indexes() -> dict[str, int]:
    """Build both persistent indexes and return their chunk counts."""
    documents = load_documents()
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return {
        "fixed": index_strategy(client, model, documents, "fixed"),
        "sentence": index_strategy(client, model, documents, "sentence"),
    }


if __name__ == "__main__":
    counts = build_indexes()
    print(f"Indexed {counts['fixed']} fixed-size chunks in cred_fixed_chunks")
    print(f"Indexed {counts['sentence']} sentence chunks in cred_sentence_chunks")
