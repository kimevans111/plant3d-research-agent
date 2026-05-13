# Skill Layer Development Report

## 1. Added files

- `skills/README.md`
- `skills/__init__.py`
- `skills/schemas.py`
- `skills/registry.py`
- `skills/selector.py`
- `skills/executor.py`
- `skills/*/SKILL.md`
- `skills/*/schema.json`
- `skills/*/examples.md`
- `scripts/demo_skill_selection.py`
- `tests/test_skill_registry.py`
- `tests/test_skill_selector.py`
- `tests/test_skill_executor.py`
- `docs/SKILL_LAYER_ANALYSIS.md`
- `docs/SKILL_LAYER_GUIDE.md`
- `docs/SKILL_LAYER_DEVELOPMENT_REPORT.md`

## 2. Modified files

- `app/schemas.py`
- `app/main.py`
- `frontend/streamlit_app.py`
- `README.md`

## 3. Designed Skills

- `training_log_analysis`
- `rag_research_qa`
- `rag_evaluation`
- `report_generation`
- `plant3d_domain_explanation`

## 4. Skill and Tool distinction

Tool is a concrete callable action, such as `parse_training_log` or `rag_retrieve_context`. Skill is the reusable workflow boundary that decides when those tools are relevant, what schema they require, and how failures should be handled.

## 5. SkillSelector rules

- Training/log/metric terms plus training file suffixes select `training_log_analysis`.
- RAG-Eval, source hit, citation hit, top-k, and failure-case terms select `rag_evaluation`.
- Document, notes, paper, citation, source, and retrieval terms select `rag_research_qa`.
- Report, Markdown, export, and summary terms select `report_generation`.
- Plant3D, leaf-stem, thin stem, point cloud, mIoU, F1, and phenotyping terms select `plant3d_domain_explanation`.
- Unknown queries fall back to `rag_research_qa`.

## 6. Run demo

```bash
python scripts/demo_skill_selection.py --query "为什么我的 F1 后期震荡？"
python scripts/demo_skill_selection.py --query "运行 RAG-Eval 看 citation hit 是否可靠"
python scripts/demo_skill_selection.py --query "Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？"
```

## 7. Run tests

```bash
pytest
```

Latest local verification: `28 passed`.

## 8. Current limitations

- The executor returns a selected Skill and recommended tool plan, but it does not replace the existing Agent runtime.
- Selection is rule-based and may misclassify ambiguous queries.
- Skills are local definitions, not MCP tools.
- The implementation is not a full multi-agent or LangGraph architecture.

## 9. Future upgrades

- Direct Skill runtime execution.
- Candidate Skill ranking instead of single selection.
- Per-Skill regression traces.
- MCP adapters for selected tools.
- LangGraph orchestration if workflow branching becomes complex.
- Memory Skill for experiment history.

## 10. Public positioning

Describe the module as a lightweight Skill Layer with schema-driven capability definitions, a rule-based selector, a traceable tool plan, and pytest/API/Streamlit integration. Do not claim full multi-agent runtime, MCP implementation, or LangGraph migration.

## 11. Technical explanation

Explain that the project already had tools. The Skill Layer adds an engineering boundary above those tools so the Agent can choose a capability, inspect its schema, and produce an auditable tool plan before execution.
