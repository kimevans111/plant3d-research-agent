# Plant3D Domain Explanation Skill

## Purpose

Explain 3D plant point cloud segmentation and phenotyping concepts, then connect those concepts to experiment analysis when evidence is available.

## When to use

Use this skill when the user asks about leaf-stem boundary confusion, thin stem missing, mIoU, OA, F1, Precision, Recall, leaf counting, plant height, point cloud segmentation failure cases, or paper-style experiment wording.

## Inputs

- `query`: domain question.
- `metrics`: optional observed experiment metrics.
- `citations`: optional retrieved source evidence.
- `context`: optional user-provided experiment context.
- `task_type`: optional explicit route.

## Outputs

- Concept explanation.
- Evidence used, if any.
- Unknowns or missing data.
- Optional report-ready wording.

## Domain concepts

- 3D plant point cloud segmentation.
- Leaf/stem class-wise IoU.
- Leaf-stem boundary confusion.
- Thin stem missing.
- mIoU, OA, Precision, Recall, and F1-score.
- Phenotyping outputs such as leaf count and plant height.

## Constraints

- Do not invent experiment results.
- Concept explanations may use general domain knowledge.
- Concrete conclusions about a run must come from user input, parser output, or citations.
- If metrics are missing, state that quantitative comparison is unavailable.

## Example queries

- "解释 leaf-stem boundary confusion。"
- "thin stem missing 是什么失败案例？"
- "mIoU 与 F1 有什么区别？"
- "为什么 stem IoU 低？"
- "把实验结果转成论文式表达。"

## Engineering notes

- This skill isolates domain explanation from retrieval and metric parsing.
- It helps the Agent avoid mixing conceptual explanation with unsupported experiment claims.
- It can optionally call RAG retrieval when the answer must be grounded in project notes.
- It keeps domain language reusable across reports, QA, and training diagnosis.
