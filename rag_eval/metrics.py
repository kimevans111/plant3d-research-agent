"""String-based metrics for RAG-Eval Mini."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable


def normalize_text(value: str) -> str:
    """Normalize text for case-insensitive and whitespace-insensitive matching."""
    lowered = value.lower()
    lowered = re.sub(r"[_\-]+", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def source_name(value: str) -> str:
    """Normalize a source path to its comparable file name."""
    return normalize_text(Path(value).name)


def source_hit_at_k(retrieved_sources: Iterable[str], expected_sources: Iterable[str]) -> int:
    """Return 1 when any expected source appears in retrieved top-k sources."""
    expected = {source_name(item) for item in expected_sources if item}
    retrieved = {source_name(item) for item in retrieved_sources if item}
    if not expected:
        return 0
    return int(bool(expected & retrieved))


def _contains_phrase(corpus: str, phrase: str) -> bool:
    normalized_phrase = normalize_text(phrase)
    if not normalized_phrase:
        return False
    if normalized_phrase in corpus:
        return True
    tokens = [token for token in re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", normalized_phrase) if token]
    if not tokens:
        return False
    return all(token in corpus for token in tokens)


def keyword_recall(expected_keywords: Iterable[str], texts: Iterable[str] | str) -> float:
    """Return the fraction of expected keywords found in retrieved chunks or answer text."""
    keywords = [item for item in expected_keywords if item]
    if not keywords:
        return 0.0
    if isinstance(texts, str):
        corpus = normalize_text(texts)
    else:
        corpus = normalize_text("\n".join(texts))
    hits = sum(1 for keyword in keywords if _contains_phrase(corpus, keyword))
    return hits / len(keywords)


def missing_keywords(expected_keywords: Iterable[str], texts: Iterable[str] | str) -> list[str]:
    """Return expected keywords that were not found in the provided text."""
    if isinstance(texts, str):
        corpus = normalize_text(texts)
    else:
        corpus = normalize_text("\n".join(texts))
    return [keyword for keyword in expected_keywords if keyword and not _contains_phrase(corpus, keyword)]


def citation_hit(citations: Iterable[dict[str, Any]] | Iterable[str], expected_sources: Iterable[str]) -> int:
    """Return 1 when citation sources include any expected source."""
    sources: list[str] = []
    for citation in citations:
        if isinstance(citation, dict):
            source = citation.get("source") or citation.get("metadata", {}).get("source")
            if source:
                sources.append(str(source))
        elif citation:
            sources.append(str(citation))
    return source_hit_at_k(sources, expected_sources)


def answer_point_coverage(answer: str, expected_answer_points: Iterable[str]) -> float:
    """Return the fraction of expected answer points covered by the answer text."""
    points = [item for item in expected_answer_points if item]
    if not points:
        return 0.0
    corpus = normalize_text(answer)
    hits = sum(1 for point in points if _contains_phrase(corpus, point))
    return hits / len(points)


def retrieval_empty_rate(empty_flags: Iterable[bool]) -> float:
    """Return the ratio of questions that had no retrieved chunks."""
    flags = list(empty_flags)
    if not flags:
        return 0.0
    return sum(1 for flag in flags if flag) / len(flags)


def average_score(scores: dict[str, float | int | None]) -> float:
    """Average available per-question quality metrics with safe fallbacks."""
    keys = ["source_hit_at_k", "keyword_recall", "citation_hit", "answer_point_coverage"]
    values = [float(scores[key]) for key in keys if scores.get(key) is not None]
    if not values:
        return 0.0
    return sum(values) / len(values)


def round_metric(value: float | int, digits: int = 4) -> float:
    """Round a metric for stable JSON and Markdown output."""
    return round(float(value), digits)
