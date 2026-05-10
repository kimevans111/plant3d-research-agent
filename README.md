# Plant3D Research Agent

AI Agent for 3D plant point cloud experiment analysis with RAG, tool calling, training-log parsing, plotting, and Markdown report generation.

Plant3D Research Agent is a runnable MVP for 3D plant point cloud segmentation experiment analysis. It combines FastAPI, Streamlit, rule-based tool calling, local RAG, plotting, and Markdown report generation to help analyze training logs, experiment tables, research notes, and segmentation results.

The system is designed around plant phenotyping research workflows: Plant-GeoAT, PointNet++, DGCNN, PointTransformerV3, PointVector, PointLIBR, mIoU, OA, Precision, Recall, F1-score, class-wise IoU, leaf IoU, stem IoU, RMSE, MAE, and R2.

## Highlights

- FastAPI + Streamlit runnable MVP for experiment analysis workflows.
- Rule-based tool calling for log parsing, metric diagnosis, plotting, and report generation.
- Local RAG over research notes with mock LLM fallback, so the demo runs without API keys.
- Docker, tests, sample data, and technical documentation included.

## Quick Start

```bash
pip install -r requirements.txt
python scripts/run_demo.py
```

## Features

- Upload `.txt`, `.log`, `.md`, `.csv`, `.json`, and optional `.pdf` files.
- Parse training logs with tolerant regular expressions.
- Extract epoch, train/val loss, mIoU, mAcc, OA, Precision, Recall, F1, leaf IoU, stem IoU, best mIoU, best F1, and best epoch.
- Diagnose overfitting, training fluctuation, class imbalance, and leaf/stem IoU gaps.
- Generate mIoU, F1, and loss curves with Matplotlib.
- Build a RAG knowledge base over uploads using a stable local JSON vector store by default, with an implemented Chroma backend available through configuration.
- Answer research questions with retrieved context and source snippets.
- Generate Markdown reports under `reports/`.
- Run without API keys through mock LLM and local hashing embeddings.

## Documentation

- `docs/ARCHITECTURE.md`: architecture, data flow, Agent workflow, Tool Calling, and RAG.
- `docs/AGENT_TRACE.md`: sample Agent execution trace.
- `docs/DEMO_OUTPUT.md`: expected command-line demo output.

## Directory Structure

```text
Plant3D-Research-Agent/
├── app/
├── agent/
├── rag/
├── tools/
├── llm/
├── frontend/
├── examples/
├── tests/
├── uploads/
├── reports/
├── docker/
├── docs/
├── scripts/
├── .env.example
├── docker-compose.yml
├── requirements.txt
├── AGENTS.md
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

Python 3.10+ is recommended.

## Environment

Copy the example file and edit it if you want to use an OpenAI-compatible provider:

```bash
copy .env.example .env
```

Default mode uses no external API:

```env
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
BACKEND_URL=http://localhost:8000
RAG_PERSIST_DIR=.rag_index
RAG_VECTOR_BACKEND=simple
```

For OpenAI, DeepSeek, Qwen, or another compatible service, set `LLM_PROVIDER=openai-compatible`, provide `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`.

For Chroma, set `RAG_VECTOR_BACKEND=chroma`. The default `simple` backend uses deterministic local embeddings and keeps the MVP runnable in restricted environments.

## Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the API docs at:

```text
http://localhost:8000/docs
```

## Run Frontend

```bash
streamlit run frontend/streamlit_app.py
```

Then open the Streamlit URL printed by the command.

## One-Command Demo

Run the local sample workflow without starting the web UI:

```bash
python scripts/run_demo.py
```

On Windows PowerShell, backend and frontend helper scripts are available:

```powershell
.\scripts\run_backend.ps1
.\scripts\run_frontend.ps1
```

## Example Workflow

1. Start the FastAPI backend.
2. Start the Streamlit frontend.
3. Upload `examples/sample_train.log`.
4. Click `Analyze Log`.
5. Review the metric summary, diagnosis, suggestions, generated figures, and Markdown report download.
6. Upload `examples/sample_paper_notes.md`.
7. Click `Build RAG Knowledge Base`.
8. Ask:

```text
Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？
```

The system retrieves relevant notes and answers with source snippets.

## Analyze A Training Log Via API

Upload a file:

```bash
curl -F "file=@examples/sample_train.log" http://localhost:8000/upload
```

Analyze it:

```bash
curl -X POST http://localhost:8000/analyze-log ^
  -H "Content-Type: application/json" ^
  -d "{\"filename\":\"sample_train.log\"}"
```

On macOS/Linux, replace `^` with `\`.

## Build RAG Knowledge Base

```bash
curl -X POST http://localhost:8000/build-index ^
  -H "Content-Type: application/json" ^
  -d "{}"
```

Ask a question:

```bash
curl -X POST http://localhost:8000/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？\"}"
```

## Tests

```bash
pytest
```

Current tests cover:
- training log parsing
- metric analysis
- Markdown report generation
- FastAPI health/upload/analyze endpoints
- RAG index build and retrieval smoke flow

## Docker

Build:

```bash
docker build -f docker/Dockerfile -t plant3d-research-agent .
```

Run:

```bash
docker run --rm -p 8000:8000 plant3d-research-agent
```

Run backend and Streamlit together:

```bash
docker compose up --build
```

Then open:

- API: <http://localhost:8000/docs>
- Streamlit: <http://localhost:8501>

## MVP Limitations

- PDF loading is basic and depends on `pypdf`.
- RAG uses deterministic hashing embeddings by default; semantic quality can be improved with stronger embeddings.
- Tool calling is implemented as lightweight Python orchestration rather than a heavy agent framework.
- The Streamlit UI focuses on usability rather than advanced dashboard styling.

## TODO

- Add OpenAI-compatible embedding providers.
- Add richer experiment table comparison and automatic ablation summaries.
- Add segmentation result visualization for point clouds.
- Add confusion-matrix and class-wise IoU plots.
- Add persistent experiment registry.
- Add report templates closer to journal paper result sections.
- Add more tests for FastAPI endpoints and RAG retrieval quality.
