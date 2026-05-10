# RAG-Eval Mini Guide

## Why RAG Evaluation Matters

RAG is only useful when retrieval brings the right evidence into the answer path. A demo that returns fluent answers is not enough for a research assistant: it also needs evidence that the correct source file was retrieved, the relevant technical terms appeared in context, and citations point back to the right document.

RAG-Eval Mini evaluates the Plant3D Research Agent document-QA flow with deterministic, lightweight metrics. It is intentionally small enough to run without API keys and without network access.

## Metrics Used In This Project

| Metric | What it checks | Why it matters |
| --- | --- | --- |
| `source_hit_at_k` | Whether top-k retrieved chunks include an expected source file. | Tests retrieval recall at the document/source level. |
| `keyword_recall` | How many expected keywords appear in retrieved chunks or answer text. | Checks whether the retrieved evidence contains key domain concepts. |
| `citation_hit` | Whether citations reference expected source files. | Checks whether citation metadata is bound to retrieval results correctly. |
| `answer_point_coverage` | How many expected answer points are covered. | Gives a simple quality signal for generated or extractive answers. |
| `retrieval_empty_rate` | How often retrieval returns no chunks. | Catches indexing, loading, and backend failures. |
| `average_score` | Mean of source hit, keyword recall, citation hit, and answer coverage. | Gives a quick ranking signal for failure-case triage. |

## Why MVP Does Not Use LLM-as-Judge

This module avoids LLM-as-judge in the MVP because:

- It must run without API keys.
- It should be deterministic enough for pytest and CI.
- Retrieval failures should be visible before generation quality is judged.
- String metrics are easy to explain, debug, and reproduce in a lightweight research prototype.

LLM-as-judge can be added later for semantic answer grading, but it should complement source and citation metrics rather than replace them.

## How To Run

```bash
python -m rag_eval.cli \
  --eval-file examples/eval/rag_eval_questions.jsonl \
  --docs-dir examples \
  --top-k 3 \
  --output-dir reports/rag_eval \
  --use-agent-answer false \
  --retriever auto \
  --rebuild-index true
```

Supported retriever modes:

- `auto`: use the existing project RAG backend configuration.
- `json`: force the local JSON vector store.
- `chroma`: attempt Chroma and fall back to local JSON if unavailable.
- `keyword`: deterministic keyword-overlap baseline.

## How To Interpret Results

Low `source_hit_at_k` means the expected file did not appear in top-k. Start by checking chunk size, overlap, source metadata, and top_k.

Low `keyword_recall` means the retrieved context missed important domain terms. Try query rewriting, hybrid search, better embeddings, or richer eval questions.

Low `citation_hit` means the answer path may not preserve source metadata. Check how retrieved chunks are converted into `citations`.

Low `answer_point_coverage` means the answer or retrieved context did not cover expected reasoning points. If retrieval is good, improve prompt construction or context formatting.

High `retrieval_empty_rate` usually indicates index build failure, unsupported file types, wrong `docs_dir`, or a stale persist directory.

## Engineering Value

RAG-Eval Mini turns the RAG workflow into an inspectable engineering system. It evaluates retrieval before generation, treats citation correctness as a first-class metric, keeps the module runnable without API keys, and converts failure cases into concrete tuning suggestions.

## Upgrade Path

- Add real embedding providers and compare them with hashing embeddings.
- Add rerankers for top-k refinement.
- Add hybrid search that combines keyword and vector scores.
- Expand the eval set with more manually labeled questions.
- Add LLM-as-judge for semantic answer quality after deterministic metrics are stable.
- Store query, retrieval, citation, answer, and report traces for regression tracking.
- Add trend reports to compare retrieval quality across commits.
