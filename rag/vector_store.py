"""Vector store backends for Chroma with a lightweight local fallback."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Protocol

import numpy as np

from rag.document_loader import Document


class SearchBackend(Protocol):
    """Minimal vector-store interface used by the retriever."""

    backend_name: str

    def reset(self) -> None:
        ...

    def add_documents(self, documents: list[Document]) -> None:
        ...

    def similarity_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        ...


class HashingEmbeddingProvider:
    """Deterministic token hashing embeddings that require no external model."""

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vector = np.zeros(self.dim, dtype=np.float32)
        tokens = re.findall(r"[A-Za-z0-9_+\-.]+|[\u4e00-\u9fff]", text.lower())
        if not tokens:
            return vector.tolist()
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = float(np.linalg.norm(vector))
        if norm > 0:
            vector /= norm
        return vector.tolist()


class SimpleJsonVectorStore:
    """Local JSON vector store used when Chroma is not available."""

    backend_name = "simple-json"

    def __init__(self, persist_dir: str | Path, embedding_provider: HashingEmbeddingProvider | None = None) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.persist_dir / "index.json"
        self.embedding_provider = embedding_provider or HashingEmbeddingProvider()
        self.records: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not self.index_path.exists():
            self.records = []
            return
        try:
            self.records = json.loads(self.index_path.read_text(encoding="utf-8"))
        except Exception:
            self.records = []

    def _save(self) -> None:
        self.index_path.write_text(json.dumps(self.records, ensure_ascii=False, indent=2), encoding="utf-8")

    def reset(self) -> None:
        self.records = []
        self._save()

    def add_documents(self, documents: list[Document]) -> None:
        existing_ids = {rec["id"] for rec in self.records}
        for index, document in enumerate(documents):
            metadata = _sanitize_metadata(document.metadata)
            doc_id = f"{metadata.get('source', 'doc')}-{metadata.get('chunk_id', index)}"
            if doc_id in existing_ids:
                continue
            existing_ids.add(doc_id)
            self.records.append(
                {
                    "id": doc_id,
                    "text": document.text,
                    "metadata": metadata,
                    "embedding": self.embedding_provider.embed(document.text),
                }
            )
        self._save()

    def similarity_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not self.records:
            self._load()
        query_vector = np.array(self.embedding_provider.embed(query), dtype=np.float32)
        results: list[dict[str, Any]] = []
        for record in self.records:
            vector = np.array(record.get("embedding", []), dtype=np.float32)
            score = float(np.dot(query_vector, vector)) if vector.size else 0.0
            if not math.isfinite(score):
                score = 0.0
            metadata = record.get("metadata", {})
            results.append(
                {
                    "text": record.get("text", ""),
                    "chunk": record.get("text", ""),
                    "source": metadata.get("source", "unknown"),
                    "metadata": metadata,
                    "score": score,
                }
            )
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


class ChromaVectorStore:
    """Chroma-backed vector store using local deterministic embeddings."""

    backend_name = "chroma"

    def __init__(
        self,
        persist_dir: str | Path,
        collection_name: str = "plant3d_research_agent",
        embedding_provider: HashingEmbeddingProvider | None = None,
    ) -> None:
        import chromadb

        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider or HashingEmbeddingProvider()
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents: list[Document]) -> None:
        if not documents:
            return
        ids: list[str] = []
        texts: list[str] = []
        metadatas: list[dict[str, str | int | float | bool]] = []
        embeddings: list[list[float]] = []
        for index, document in enumerate(documents):
            metadata = _sanitize_metadata(document.metadata)
            ids.append(f"{metadata.get('source', 'doc')}-{metadata.get('chunk_id', index)}")
            texts.append(document.text)
            metadatas.append(metadata)
            embeddings.append(self.embedding_provider.embed(document.text))
        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def similarity_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self.collection.count() == 0:
            return []
        result = self.collection.query(
            query_embeddings=[self.embedding_provider.embed(query)],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        results: list[dict[str, Any]] = []
        for doc, metadata, distance in zip(docs, metadatas, distances):
            score = 1.0 / (1.0 + float(distance)) if distance is not None else 0.0
            results.append(
                {
                    "text": doc,
                    "chunk": doc,
                    "source": metadata.get("source", "unknown") if metadata else "unknown",
                    "metadata": metadata or {},
                    "score": score,
                }
            )
        return results


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    clean: dict[str, str | int | float | bool] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            clean[key] = value
        elif value is not None:
            clean[key] = str(value)
    return clean


def create_vector_store(persist_dir: str | Path = ".rag_index", prefer_chroma: bool | None = None) -> SearchBackend:
    """Create the configured vector store.

    `RAG_VECTOR_BACKEND=chroma` enables Chroma explicitly. The default local JSON
    backend is intentionally conservative because Chroma can fail in constrained
    demo environments while the MVP must remain runnable without special setup.
    """
    backend = os.getenv("RAG_VECTOR_BACKEND", "simple").lower()
    should_try_chroma = backend == "chroma" or (backend == "auto" and prefer_chroma)
    if should_try_chroma:
        try:
            return ChromaVectorStore(persist_dir)
        except Exception:
            pass
    return SimpleJsonVectorStore(persist_dir)
