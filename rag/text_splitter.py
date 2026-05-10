"""Text chunking utilities for the RAG pipeline."""

from __future__ import annotations

from dataclasses import replace

from rag.document_loader import Document


def split_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks with paragraph-aware boundaries."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    normalized = text.replace("\r\n", "\n")
    paragraphs = [part.strip() for part in normalized.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs or [normalized.strip()]:
        if not paragraph:
            continue
        if len(paragraph) > chunk_size:
            start = 0
            while start < len(paragraph):
                end = start + chunk_size
                chunks.append(paragraph[start:end].strip())
                if end >= len(paragraph):
                    break
                start = max(end - overlap, start + 1)
            continue

        separator = "\n\n" if current else ""
        candidate = f"{current}{separator}{paragraph}"
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            tail = current[-overlap:] if current and overlap else ""
            current = f"{tail}\n\n{paragraph}".strip() if tail else paragraph

    if current.strip():
        chunks.append(current.strip())
    return chunks


def split_documents(
    documents: list[Document],
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[Document]:
    """Split loaded documents and preserve source metadata."""
    chunks: list[Document] = []
    for document in documents:
        for chunk_id, chunk in enumerate(split_text(document.text, chunk_size, overlap)):
            metadata = dict(document.metadata)
            metadata["chunk_id"] = chunk_id
            chunks.append(replace(document, text=chunk, metadata=metadata))
    return chunks
