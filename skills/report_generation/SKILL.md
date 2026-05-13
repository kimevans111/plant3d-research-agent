# Report Generation Skill

## Purpose

Generate Markdown reports that combine training metrics, diagnosis, figures, RAG citations, RAG evaluation results, and experiment summaries.

## When to use

Use this skill when the user asks to generate, export, download, summarize, or format a Markdown report for a training log, RAG evaluation run, model comparison, or research answer.

## Inputs

- `query`: report instruction.
- `metrics`: optional parsed or summarized metrics.
- `figures`: optional figure paths.
- `citations`: optional citation records.
- `rag_eval_result`: optional RAG-Eval result dictionary.
- `output_dir`: optional output directory.

## Outputs

- Markdown report path.
- Report sections produced.
- Missing items or skipped figures.
- `used_tools` trace.

## Report template

Reports should generally include:

1. Overview.
2. Data sources.
3. Key metrics or RAG-Eval summary.
4. Diagnosis or failure cases.
5. Figures when available.
6. Citations or source files.
7. Suggested next steps.

## Failure handling

- Missing metrics are marked as unavailable.
- Missing figure paths are skipped or reported.
- Empty citations are shown as "no retrieved source".
- Partial reports are allowed if the input data is incomplete.

## Constraints

- Reports must identify data sources.
- Do not invent missing metrics or experiment results.
- Generated prose must distinguish observed evidence from suggested interpretation.
- The skill must run without an API key.

## Example queries

- "生成训练日志分析报告。"
- "生成 RAG 评估报告。"
- "把两个模型的结果生成对比报告。"
- "把结果写成论文式描述。"
- "报告缺少图表时应该怎么处理？"

## Engineering notes

- This skill turns raw tool outputs into a reproducible artifact.
- It enforces data-source visibility and avoids silently inventing missing values.
- It can reuse both training-log and RAG-Eval outputs without coupling those modules together.
- It is a good example of a skill that composes tools rather than replacing them.
