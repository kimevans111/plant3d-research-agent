# Skill Layer Guide

## 1. What is a Skill?

A Skill is a reusable capability boundary. It is larger than one function, but smaller than a full independent Agent. In this project, each Skill has documentation, a JSON schema, internal tool recommendations, constraints, failure handling, and examples.

## 2. Why this project fits a Skill design

Plant3D Research Agent already has several repeated workflows: training-log analysis, RAG research QA, RAG evaluation, report generation, and domain explanation. These workflows are stable enough to name as Skills, but they do not require a heavy framework.

## 3. Current Skills

| Skill | Responsibility |
| --- | --- |
| `training_log_analysis` | Parse logs, summarize metrics, diagnose training issues, plot curves, and prepare reports. |
| `rag_research_qa` | Retrieve research-document context and answer with citations. |
| `rag_evaluation` | Measure source hit, keyword recall, citation hit, answer coverage, empty retrieval, and failure cases. |
| `report_generation` | Turn tool outputs into Markdown artifacts. |
| `plant3d_domain_explanation` | Explain Plant3D segmentation and phenotyping concepts without inventing experiment results. |

## 4. Registry, Selector, Executor

- `SkillRegistry` loads `SKILL.md` and `schema.json` files from `skills/*`.
- `SkillSelector` uses keyword and file-type rules to choose a Skill.
- `SkillExecutor` returns the selected Skill, confidence, reason, recommended tools, and a trace.

## 5. Skill and Tool Calling

Tool Calling executes concrete actions. Skill selection decides which workflow should own the request. For example, `training_log_analysis` may call `parse_training_log`, `summarize_metrics`, and `generate_training_curves`.

## 6. Skill and MCP

MCP can expose tools or resources across processes. This project does not implement MCP. The current Skill Layer is local Python code and Markdown/JSON definitions. It could later map Skill tools to MCP tools.

## 7. Skill and Sub-Agent

A Sub-Agent has its own planning loop and execution state. A Skill is a named workflow boundary. This project implements Skills, not full Sub-Agents.

## 8. Current project boundary

- Not a complete multi-agent architecture.
- No mandatory LangGraph dependency.
- No MCP runtime.
- No LLM-based router.
- Designed to run without API keys.

## 9. Upgrade roadmap

- Add a Skill runtime that can call selected tools directly.
- Convert Skills into LangGraph nodes if graph orchestration becomes useful.
- Expose selected tools through MCP.
- Add a Memory Skill for experiment history.
- Add an Agent-Eval Skill for end-to-end task quality.
- Add per-Skill regression tests and trace persistence.
