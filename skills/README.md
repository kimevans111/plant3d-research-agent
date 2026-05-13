# Skill Layer

This directory contains a lightweight Skill Layer for Plant3D Research Agent.

The goal is to make the existing capabilities easier to reason about without replacing the current Agent runtime:

- **Skill**: a reusable capability with a purpose, input/output schema, internal tools, failure handling, and examples.
- **Tool**: a concrete callable action such as `parse_training_log`, `rag_retrieve_context`, or `generate_markdown_report`.
- **Agent**: the orchestrator that interprets a user request and decides which capability to use.
- **Sub-Agent**: an independent agent with its own planning loop. This project does not implement full sub-agents.

Current skills:

| Skill | Purpose |
| --- | --- |
| `training_log_analysis` | Parse logs, summarize metrics, diagnose training issues, and prepare reports. |
| `rag_research_qa` | Answer research questions with retrieved context and source citations. |
| `rag_evaluation` | Evaluate retrieval quality, citation hit, keyword recall, and failure cases. |
| `report_generation` | Assemble Markdown reports from metrics, figures, citations, and eval outputs. |
| `plant3d_domain_explanation` | Explain 3D plant point cloud segmentation and phenotyping concepts. |

The runtime is intentionally small:

- `registry.py` loads `SKILL.md` and `schema.json`.
- `selector.py` selects a skill with transparent keyword rules.
- `executor.py` returns the selected skill, confidence, recommended tools, and trace.

Run a local demo:

```bash
python scripts/demo_skill_selection.py --query "为什么我的 F1 后期震荡？"
```
