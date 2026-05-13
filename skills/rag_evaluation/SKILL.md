# RAG Evaluation Skill

## Purpose

Evaluate RAG retrieval and answer reliability for research-document QA. This skill measures whether retrieval finds expected sources, whether citations are correct, and which queries fail.

## When to use

Use this skill when the user asks how well RAG works, wants to compare `top_k`, checks citation reliability, reviews failure cases, or generates a RAG-Eval report.

## Inputs

- `eval_file`: JSONL evaluation set.
- `docs_dir`: document directory.
- `top_k`: retrieval depth.
- `retriever`: `auto`, `keyword`, `json`, or `chroma`.
- `use_agent_answer`: whether to call answer generation.
- `rebuild_index`: whether to rebuild the index before evaluation.

## Outputs

- Summary metrics.
- Per-question detailed results.
- Metrics by category.
- Failure cases.
- JSON artifacts and Markdown report path.

## Metrics

- `source_hit@k`: whether top-k retrieved chunks include expected sources.
- `keyword recall`: fraction of expected keywords found in retrieved chunks or answer.
- `citation hit`: whether citations point to expected sources.
- `answer point coverage`: fraction of expected answer points matched.
- `retrieval empty rate`: fraction of questions with no retrieved chunks.
- `failure case analysis`: low-scoring questions with possible fixes.

## Execution steps

1. Load and validate eval questions.
2. Run retrieval for each question.
3. Optionally generate an Agent answer.
4. Compute deterministic string/metadata-based metrics.
5. Aggregate summary and category metrics.
6. Save detail JSON, summary JSON, and Markdown report.

## Failure cases

- Expected source missing from top-k.
- Retrieved chunks do not contain expected keywords.
- Citation source does not match retrieved source metadata.
- Answer misses expected answer points.
- Retrieval returns no chunks.

## Constraints

- This is lightweight evaluation, not a full semantic judge.
- Do not overstate string-match metrics as human-level answer grading.
- If real embeddings or Chroma are unavailable, report fallback/local retrieval behavior.
- The skill must run without network access or an API key.

## Example queries

- "运行 RAG-Eval，看看 source_hit@k 怎么样。"
- "比较 top_k=3 和 top_k=5 的 citation hit。"
- "列出 RAG 检索失败案例。"
- "citation hit 低应该怎么优化？"
- "keyword recall 低说明什么？"

## Engineering notes

- This skill shows that RAG quality is measurable beyond a single demo answer.
- It uses simple deterministic metrics first because they are reproducible and CI-friendly.
- It separates retrieval failure from answer generation failure.
- It creates a practical path to later add embeddings, reranking, hybrid search, and LLM-as-judge.
