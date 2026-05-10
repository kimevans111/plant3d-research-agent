"""Document loading for uploads and examples used by the RAG pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd


SUPPORTED_EXTENSIONS = {".txt", ".log", ".md", ".csv", ".json", ".pdf"}


@dataclass(slots=True)
class Document:
    """A loaded text document with source metadata."""

    text: str
    source: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


def _load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return "[PDF support requires pypdf. Install dependencies from requirements.txt to enable PDF loading.]"

    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    except Exception as exc:
        return f"[Failed to read PDF {path.name}: {exc}]"


def load_document(path: str | Path) -> Document | None:
    """Load a supported document file into plain text."""
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return None

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return None

    try:
        if suffix == ".csv":
            frame = pd.read_csv(file_path)
            text = frame.to_csv(index=False)
        elif suffix == ".json":
            obj = json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
            text = json.dumps(obj, ensure_ascii=False, indent=2)
        elif suffix == ".pdf":
            text = _load_pdf(file_path)
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        text = f"[Failed to load {file_path.name}: {exc}]"

    return Document(
        text=text,
        source=file_path.name,
        metadata={
            "source": file_path.name,
            "path": str(file_path),
            "suffix": suffix,
            "size": file_path.stat().st_size,
        },
    )


def iter_supported_files(path_or_paths: str | Path | Iterable[str | Path]) -> list[Path]:
    """Collect supported files from one path, one directory, or a path iterable."""
    if isinstance(path_or_paths, (str, Path)):
        paths = [Path(path_or_paths)]
    else:
        paths = [Path(item) for item in path_or_paths]

    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            for candidate in sorted(path.rglob("*")):
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                    files.append(candidate)
        elif path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
    return files


def load_documents(path_or_paths: str | Path | Iterable[str | Path]) -> list[Document]:
    """Load all supported files from the given path input."""
    documents: list[Document] = []
    for path in iter_supported_files(path_or_paths):
        document = load_document(path)
        if document and document.text.strip():
            documents.append(document)
    return documents
