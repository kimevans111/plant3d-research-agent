# AGENTS.md

## Project

Plant3D Research Agent is an AI Agent system for 3D plant point cloud segmentation experiment analysis.

The project focuses on:
- deep learning training log analysis
- RAG over research notes and experiment files
- tool calling for metrics extraction and plotting
- automatic Markdown report generation
- plant point cloud segmentation research workflows

## Coding Rules

- Use Python 3.10+.
- Use pathlib.Path for file paths.
- Do not hard-code API keys.
- Read API keys from .env.
- Keep the project runnable without API keys by using mock or fallback providers.
- Prefer simple, maintainable MVP implementation over excessive abstraction.
- Add type hints to core functions.
- Add docstrings to public functions.
- Do not put all logic into one file.
- Keep FastAPI backend, Streamlit frontend, tools, rag, llm, and agent modules separated.
- All generated reports should be saved under reports/.
- All generated figures should be saved under reports/figures/.
- Uploaded files should be saved under uploads/.
- Example files should be placed under examples/.
- Tests should be placed under tests/.

## Testing

Before finishing a task, run:

```bash
pytest
```

If dependencies are missing or tests fail, explain the reason and fix the issue when possible.

## Domain Context

The user studies 3D plant point cloud semantic segmentation and automated phenotyping.

Common models:
- Plant-GeoAT
- PointNet++
- DGCNN
- PointTransformerV3
- PointVector
- PointLIBR

Common metrics:
- mIoU
- OA
- mAcc
- Precision
- Recall
- F1-score
- class-wise IoU
- leaf IoU
- stem IoU
- RMSE
- MAE
- R2

Common research problems:
- leaf-stem boundary confusion
- thin stem missing
- structural discontinuity
- occlusion
- organ overlap
- class imbalance
- training fluctuation
- overfitting
- unstable F1

## Expected Output Quality

The project should be useful as a portfolio project for AI Agent development internship applications.

Therefore, README, examples, tests, and demo usability are important.
