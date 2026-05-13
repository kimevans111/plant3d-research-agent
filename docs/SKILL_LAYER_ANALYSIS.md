# Skill Layer Analysis

## 1. Modules that can be abstracted as Skills

- `tools/log_parser.py`, `tools/metric_analyzer.py`, `tools/plotter.py`, and `tools/report_generator.py` form a natural Training Log Analysis Skill.
- `rag/document_loader.py`, `rag/text_splitter.py`, `rag/vector_store.py`, and `rag/retriever.py` form a RAG Research QA Skill.
- `rag_eval/dataset.py`, `rag_eval/metrics.py`, `rag_eval/evaluator.py`, and `rag_eval/report.py` form a RAG Evaluation Skill.
- `tools/report_generator.py` and `rag_eval/report.py` form a Report Generation Skill.
- Plant3D concepts in README, docs, examples, and RAG notes form a Plant3D Domain Explanation Skill.

## 2. Current Agent routing logic

The current routing logic lives in `agent/research_agent.py` inside `ResearchAgent.classify_task()`. It routes coarse tasks such as `log_analysis`, `report_generation`, `model_compare`, `doc_qa`, and `general_advice`.

## 3. Current used_tools trace

The `used_tools` trace is assembled in `agent/research_agent.py` by each execution path, for example `_run_log_analysis()`, `_run_model_compare()`, `_run_doc_qa()`, and `_run_general_advice()`.

## 4. Current RAG-Eval Mini location

RAG-Eval Mini lives in `rag_eval/`:

- `dataset.py`: JSONL eval question loading and validation.
- `metrics.py`: source hit, keyword recall, citation hit, answer coverage, and average score.
- `evaluator.py`: end-to-end evaluation runner.
- `report.py`: Markdown report generation.
- `cli.py`: command-line interface.

## 5. Current report generation modules

Training and experiment reports use `tools/report_generator.py`. RAG evaluation reports use `rag_eval/report.py`.

## 6. Whether Training Log Agent can be an independent Skill

Yes. The log parser, metric analyzer, plotting tool, and Markdown report generator already provide a clean tool chain. A Skill wrapper can describe when to use those tools, what evidence is required, and how failures should be reported.

## 7. Code that should not be heavily changed

- `agent/research_agent.py`: existing Agent behavior and `used_tools` output should remain stable.
- `rag/`: retrieval, document loading, and vector store behavior should stay compatible with RAG-Eval.
- `rag_eval/`: evaluation CLI, API, and tests should not be coupled to Skill Layer.
- `tools/`: parser and report tools should remain reusable utility functions.
- `app/main.py` and `frontend/streamlit_app.py`: only additive endpoints/UI sections should be added.

## 8. Minimal Skill Layer plan

Add a standalone `skills/` package with:

- Human-readable `SKILL.md` files.
- Machine-readable `schema.json` files.
- `SkillRegistry` for loading definitions.
- `SkillSelector` for transparent rule-based routing.
- `SkillExecutor` for returning selected skill, confidence, recommended tools, and trace.

This avoids rewriting the Agent while making capability boundaries explicit.

## 9. Existing Skill prototypes

- Training analysis prototype: parser + analyzer + plotter + report.
- RAG QA prototype: loader + splitter + retriever + citation answer path.
- RAG evaluation prototype: eval dataset + evaluator + report.
- Report generation prototype: Markdown report utilities.
- Domain explanation prototype: README/docs/examples around Plant3D concepts.

## 10. How to explain Skill Layer

The project uses Skill as a reusable capability boundary above individual tools. Tools do concrete work, such as parsing logs or retrieving chunks. The Agent decides what capability is needed. The Skill defines when it should be used, what inputs and outputs it expects, which tools it may call, and how to handle failure. This is intentionally a lightweight layer, not a full multi-agent runtime.
