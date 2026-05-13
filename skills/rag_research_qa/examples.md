# RAG Research QA Examples

## 1. Plant-GeoAT boundary question

User: "Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？"

Expected skill behavior:

- Retrieve notes about local geometry and boundary regions.
- Answer with source citations.

## 2. Metric definition

User: "mIoU 和 F1 的区别是什么？"

Expected skill behavior:

- Retrieve metric notes if available.
- Explain only supported project-specific claims with citations.

## 3. Failure case analysis

User: "点云分割中 thin stem missing 是什么问题？"

Expected skill behavior:

- Retrieve failure-case notes.
- Mention source snippets and possible causes.

## 4. Experiment setting source

User: "这个实验为什么使用 top_k=3？依据在哪里？"

Expected skill behavior:

- Search docs and notes for the setting.
- If absent, say the current documents do not contain the evidence.

## 5. Paper note QA

User: "根据 sample_paper_notes.md 说明 Plant-GeoAT 的核心方法。"

Expected skill behavior:

- Retrieve chunks from the target note.
- Return concise answer with filename citations.
