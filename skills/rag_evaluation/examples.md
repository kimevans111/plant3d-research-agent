# RAG Evaluation Examples

## 1. Run RAG-Eval

User: "运行 RAG-Eval 看 source_hit@k 和 keyword recall。"

Expected skill behavior:

- Select `rag_evaluation`.
- Load `examples/eval/rag_eval_questions.jsonl`.
- Save JSON and Markdown outputs under `reports/rag_eval/`.

## 2. Compare top_k

User: "比较 top_k=3 和 top_k=5 哪个 citation hit 更好。"

Expected skill behavior:

- Run evaluation twice or recommend two runs.
- Compare summary metrics without changing the eval set.

## 3. Inspect failure cases

User: "帮我看 RAG 失败案例。"

Expected skill behavior:

- Sort low-scoring items.
- Show expected sources, retrieved sources, missing keywords, and suggested fixes.

## 4. Low citation hit

User: "citation hit 很低怎么办？"

Expected skill behavior:

- Suggest checking source metadata, citation binding, and chunk provenance.

## 5. Low keyword recall

User: "keyword recall 低说明什么？"

Expected skill behavior:

- Explain query mismatch, weak chunking, missing docs, or insufficient retrieval depth.
