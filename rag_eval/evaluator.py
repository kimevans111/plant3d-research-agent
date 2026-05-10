"""Evaluator orchestration for RAG-Eval Mini."""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator

from agent.research_agent import ResearchAgent
from llm.provider import get_llm_provider
from rag.document_loader import load_documents
from rag.retriever import build_index, rag_retrieve_context
from rag.text_splitter import split_documents
from rag_eval.dataset import EvalQuestion, load_eval_questions
from rag_eval.metrics import (
    answer_point_coverage,
    average_score,
    citation_hit,
    keyword_recall,
    missing_keywords,
    retrieval_empty_rate,
    round_metric,
    source_hit_at_k,
)
from rag_eval.report import generate_markdown_report


RetrieverFn = Callable[[str, int], list[dict[str, Any]]]


class KeywordRetriever:
    """Small keyword-overlap retriever used as a deterministic baseline."""

    backend_name = "keyword"

    def __init__(self, docs_dir: str | Path, chunk_size: int = 900, overlap: int = 150) -> None:
        documents = load_documents(docs_dir)
        self.chunks = split_documents(documents, chunk_size=chunk_size, overlap=overlap)

    def retrieve(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Return chunks ranked by token overlap with the query."""
        query_tokens = _tokens(query)
        results: list[dict[str, Any]] = []
        for chunk in self.chunks:
            text_tokens = _tokens(chunk.text)
            overlap = len(query_tokens & text_tokens)
            score = overlap / max(len(query_tokens), 1)
            if query.lower() in chunk.text.lower():
                score += 1.0
            results.append(
                {
                    "text": chunk.text,
                    "chunk": chunk.text,
                    "source": chunk.metadata.get("source", chunk.source),
                    "metadata": chunk.metadata,
                    "score": score,
                }
            )
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


class RagEvaluator:
    """Run retrieval, citation, and answer-coverage evaluation for a RAG corpus."""

    def __init__(
        self,
        eval_file: str | Path,
        docs_dir: str | Path,
        output_dir: str | Path = "reports/rag_eval",
        top_k: int = 3,
        use_agent_answer: bool = False,
        retriever: str = "auto",
        rebuild_index: bool = False,
        persist_dir: str | Path | None = None,
        retrieval_fn: RetrieverFn | None = None,
    ) -> None:
        self.eval_file = Path(eval_file)
        self.docs_dir = Path(docs_dir)
        self.output_dir = Path(output_dir)
        self.top_k = top_k
        self.use_agent_answer = use_agent_answer
        self.retriever = retriever.lower()
        self.rebuild_index = rebuild_index
        self.persist_dir = Path(persist_dir) if persist_dir else self.output_dir / ".rag_eval_index"
        self.retrieval_fn = retrieval_fn
        self.trace: list[str] = []
        self.backend_name = self.retriever

    def run(self) -> dict[str, Any]:
        """Run evaluation and save summary, details, and Markdown report."""
        questions = load_eval_questions(self.eval_file)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        retrieve = self._prepare_retriever()

        items = [self._evaluate_question(question, retrieve) for question in questions]
        summary = self._summarize(items)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = {
            "summary": summary,
            "items": items,
            "trace": self.trace,
            "config": {
                "eval_file": str(self.eval_file),
                "docs_dir": str(self.docs_dir),
                "top_k": self.top_k,
                "use_agent_answer": self.use_agent_answer,
                "retriever": self.retriever,
                "backend": self.backend_name,
                "persist_dir": str(self.persist_dir),
            },
        }

        summary_path = self.output_dir / f"rag_eval_summary_{timestamp}.json"
        detail_path = self.output_dir / f"rag_eval_details_{timestamp}.json"
        report_path = generate_markdown_report(
            result=result,
            output_dir=self.output_dir,
            retriever_type=self.backend_name,
            top_k=self.top_k,
            use_agent_answer=self.use_agent_answer,
            mock_provider=get_llm_provider().provider_name == "mock",
            timestamp=timestamp,
        )
        summary_payload = {
            "summary": summary,
            "summary_path": str(summary_path),
            "detail_path": str(detail_path),
            "report_path": str(report_path),
            "trace": self.trace,
        }
        summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        detail_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            **summary_payload,
            "items": items,
            "metrics_by_category": summary.get("metrics_by_category", {}),
            "failure_cases": [item for item in items if item.get("average_score", 0.0) < 0.65 or item.get("failure_reason")],
        }

    def _prepare_retriever(self) -> RetrieverFn:
        if self.retrieval_fn:
            self.backend_name = "custom"
            self.trace.append("Using injected retrieval_fn.")
            return self.retrieval_fn

        if self.retriever == "keyword":
            keyword = KeywordRetriever(self.docs_dir)
            self.backend_name = keyword.backend_name
            self.trace.append(f"Loaded keyword retriever over {len(keyword.chunks)} chunks.")
            return keyword.retrieve

        backend = "simple" if self.retriever in {"json", "simple", "auto"} else self.retriever
        needs_build = self.rebuild_index or not self.persist_dir.exists() or not any(self.persist_dir.iterdir())
        if needs_build:
            with _temporary_env("RAG_VECTOR_BACKEND", backend):
                build_info = build_index(input_dir=self.docs_dir, persist_dir=self.persist_dir)
            self.backend_name = str(build_info.get("backend", backend))
            self.trace.append(
                f"Built RAG index with backend={self.backend_name}, documents={build_info.get('documents')}, chunks={build_info.get('chunks')}."
            )
        else:
            self.backend_name = backend
            self.trace.append(f"Reused existing RAG index at {self.persist_dir}.")

        def retrieve(query: str, top_k: int) -> list[dict[str, Any]]:
            with _temporary_env("RAG_VECTOR_BACKEND", backend):
                return rag_retrieve_context(query, top_k=top_k, persist_dir=self.persist_dir)

        return retrieve

    def _evaluate_question(self, question: EvalQuestion, retrieve: RetrieverFn) -> dict[str, Any]:
        retrieved = retrieve(question.question, self.top_k)
        retrieved_sources = [str(item.get("source", "unknown")) for item in retrieved]
        retrieved_texts = [str(item.get("chunk") or item.get("text") or "") for item in retrieved]
        citations: list[dict[str, Any]] = [
            {"source": source, "chunk": text, "score": item.get("score", 0.0)}
            for source, text, item in zip(retrieved_sources, retrieved_texts, retrieved)
        ]
        answer = ""

        if self.use_agent_answer and self.retriever != "keyword":
            with _temporary_env("RAG_PERSIST_DIR", str(self.persist_dir)):
                agent = ResearchAgent(reports_dir=self.output_dir, figures_dir=self.output_dir / "figures")
                agent_result = agent.run(query=question.question, task_type="doc_qa")
            answer = str(agent_result.get("answer", ""))
            citations = list(agent_result.get("citations") or citations)
        elif self.use_agent_answer:
            answer = _extractive_answer(retrieved_texts, retrieved_sources)

        eval_text = "\n".join([answer, *retrieved_texts])
        item_scores = {
            "source_hit_at_k": source_hit_at_k(retrieved_sources, question.expected_sources),
            "keyword_recall": keyword_recall(question.expected_keywords, eval_text),
            "citation_hit": citation_hit(citations, question.expected_sources),
            "answer_point_coverage": answer_point_coverage(answer or "\n".join(retrieved_texts), question.expected_answer_points),
        }
        item_average = average_score(item_scores)
        failure_reason = _failure_reason(retrieved, item_scores)
        return {
            "id": question.id,
            "question": question.question,
            "category": question.category,
            "expected_sources": question.expected_sources,
            "retrieved_sources": retrieved_sources,
            "source_hit_at_k": round_metric(item_scores["source_hit_at_k"]),
            "keyword_recall": round_metric(item_scores["keyword_recall"]),
            "citation_hit": round_metric(item_scores["citation_hit"]),
            "answer_point_coverage": round_metric(item_scores["answer_point_coverage"]),
            "average_score": round_metric(item_average),
            "retrieved_preview": [_preview(text) for text in retrieved_texts],
            "answer": answer,
            "missing_keywords": missing_keywords(question.expected_keywords, eval_text),
            "failure_reason": failure_reason,
        }

    def _summarize(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        empty_flags = [not item.get("retrieved_sources") for item in items]
        summary = {
            "num_questions": len(items),
            "source_hit_at_k": _avg(items, "source_hit_at_k"),
            "keyword_recall": _avg(items, "keyword_recall"),
            "citation_hit": _avg(items, "citation_hit"),
            "answer_point_coverage": _avg(items, "answer_point_coverage"),
            "retrieval_empty_rate": round_metric(retrieval_empty_rate(empty_flags)),
            "average_score": _avg(items, "average_score"),
        }
        summary["metrics_by_category"] = _metrics_by_category(items)
        return summary


def _avg(items: list[dict[str, Any]], key: str) -> float:
    values = [float(item.get(key, 0.0)) for item in items]
    return round_metric(sum(values) / len(values)) if values else 0.0


def _metrics_by_category(items: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[item.get("category", "unknown")].append(item)
    return {
        category: {
            "count": len(rows),
            "source_hit_at_k": _avg(rows, "source_hit_at_k"),
            "keyword_recall": _avg(rows, "keyword_recall"),
            "citation_hit": _avg(rows, "citation_hit"),
            "answer_point_coverage": _avg(rows, "answer_point_coverage"),
            "average_score": _avg(rows, "average_score"),
        }
        for category, rows in sorted(grouped.items())
    }


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text.lower()))


def _preview(text: str, max_chars: int = 280) -> str:
    compact = " ".join(text.split())
    return compact[:max_chars] + ("..." if len(compact) > max_chars else "")


def _extractive_answer(texts: list[str], sources: list[str]) -> str:
    if not texts:
        return ""
    source_list = ", ".join(sorted({source for source in sources if source}))
    return f"{texts[0][:1200]}\n\nSources: {source_list}"


def _failure_reason(retrieved: list[dict[str, Any]], scores: dict[str, float | int]) -> str | None:
    if not retrieved:
        return "No retrieved chunks."
    if scores["source_hit_at_k"] < 1:
        return "Expected source was not retrieved in top-k."
    if scores["keyword_recall"] < 0.5:
        return "Retrieved context or answer missed many expected keywords."
    if scores["citation_hit"] < 1:
        return "Citation sources did not match expected sources."
    if scores["answer_point_coverage"] < 0.5:
        return "Answer or retrieved context missed expected answer points."
    return None


@contextmanager
def _temporary_env(key: str, value: str) -> Iterator[None]:
    previous = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous
