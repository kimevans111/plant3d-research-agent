"""High-level RAG index building and retrieval helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from rag.document_loader import load_documents
from rag.text_splitter import split_documents
from rag.vector_store import create_vector_store


def default_persist_dir() -> Path:
    """Return the configured local RAG index path."""
    return Path(os.getenv("RAG_PERSIST_DIR", ".rag_index"))


def build_index(
    input_dir: str | Path = "uploads",
    persist_dir: str | Path | None = None,
    chunk_size: int = 900,
    overlap: int = 150,
) -> dict[str, Any]:
    """Build a local RAG index from supported files."""
    persist = Path(persist_dir) if persist_dir else default_persist_dir()
    documents = load_documents(input_dir)
    chunks = split_documents(documents, chunk_size=chunk_size, overlap=overlap)
    store = create_vector_store(persist)
    store.reset()
    store.add_documents(chunks)
    return {
        "backend": store.backend_name,
        "persist_dir": str(persist),
        "documents": len(documents),
        "chunks": len(chunks),
        "sources": sorted({document.source for document in documents}),
    }


def rag_retrieve_context(
    query: str,
    top_k: int = 5,
    persist_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Retrieve the top-k most relevant chunks for a user query."""
    persist = Path(persist_dir) if persist_dir else default_persist_dir()
    store = create_vector_store(persist)
    return store.similarity_search(query, top_k=top_k)
