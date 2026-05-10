# Demo Output Snapshot

This is the expected shape of `python scripts/run_demo.py`.

```text
== Plant3D Research Agent Demo ==
Indexed 3 documents into 12 chunks.

-- Log Analysis --
### 训练日志分析结果
Tools: parse_training_log, summarize_metrics, generate_training_curve, rag_retrieve_context, generate_markdown_report
Report: reports/report_sample_train_log.md

-- RAG QA --
基于检索到的笔记，Plant-GeoAT 缓解 leaf-stem boundary confusion 的核心原因是...
Tools: rag_retrieve_context
Citations: 5
```

Exact numbers may vary with chunk size, uploaded files, or vector backend.
