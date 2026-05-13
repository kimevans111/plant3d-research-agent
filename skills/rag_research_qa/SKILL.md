# RAG Research QA Skill

## Purpose

Answer research questions over papers, notes, README files, experiment records, and Markdown documents with retrieved context and source citations.

## When to use

Use this skill when the user asks about Plant-GeoAT, point cloud segmentation methods, metric definitions, experiment settings, failure cases, research notes, sources, citations, or "where does this claim come from?"

## Inputs

- `query`: user question.
- `docs_dir`: optional document directory.
- `top_k`: optional retrieval count.
- `file_paths`: optional document paths.
- `task_type`: optional explicit route such as `doc_qa`.

## Outputs

- Answer grounded in retrieved chunks.
- Citation list with source metadata.
- Retrieved source filenames.
- `used_tools` trace.

## RAG pipeline

1. Load documents with source metadata.
2. Split text into chunks.
3. Retrieve candidate chunks through local JSON vector store, Chroma, or fallback retrieval.
4. Compose an answer from retrieved context.
5. Attach citations from chunk metadata.

## Citation rule

Citations must be bound to retrieved source metadata. If a source filename is missing, return `unknown` rather than inventing a source. Do not present unsupported model-generated text as a document fact.

## Failure handling

- If retrieval is empty, state that the current knowledge base does not contain enough evidence.
- If the vector backend is unavailable, use the local fallback retriever.
- If an LLM provider is unavailable, use mock/local answer behavior or return retrieved evidence.

## Constraints

- Answers must prioritize retrieved context.
- No source-free claims should be framed as document facts.
- Retrieval and answer generation must run without an API key.
- Citation quality depends on document loader metadata and should be inspected when citations look wrong.

## Example queries

- "Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？"
- "mIoU 和 F1 的区别是什么？"
- "点云分割失败案例如何分析？"
- "这个实验设置的依据在哪里？"
- "根据论文笔记回答 Plant-GeoAT 的局部几何设计。"

## Engineering notes

- This skill is the project boundary for document-grounded QA.
- It keeps retrieval, answer generation, and citation formatting as distinct tool responsibilities.
- Empty retrieval is treated as a first-class failure mode rather than hidden by model guessing.
- It supports local fallback behavior, which makes demos and tests reproducible without an API key.
