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
- `docs/RAG_EVAL_GUIDE.md`: RAG-Eval Mini metrics, workflow, and tuning guidance.

## Directory Structure

```text
Plant3D-Research-Agent/
├── app/
├── agent/
├── rag/
├── rag_eval/
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

## RAG Evaluation

RAG-Eval Mini is a lightweight retrieval evaluation module for the research-document QA flow. It helps answer practical questions that a plain RAG demo often leaves vague:

- Did top-k retrieval include the expected source document?
- Did retrieved chunks or generated answers contain the expected technical keywords?
- Did citations point to the right source files?
- Which categories fail, such as method questions, training-log questions, or metric lookup questions?
- What should be tuned next: chunking, top_k, metadata, query rewrite, hybrid retrieval, or answer prompting?

### Eval Set Format

The bundled eval set is stored at `examples/eval/rag_eval_questions.jsonl`. Each line is one JSON object:

```json
{
  "id": "q001",
  "question": "Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？",
  "expected_keywords": ["leaf-stem boundary confusion", "local geometry"],
  "expected_sources": ["sample_paper_notes.md"],
  "expected_answer_points": ["uses local geometry features"],
  "category": "method"
}
```

The sample set contains 20 questions across `method`, `metrics`, `training_log`, `failure_case`, `phenotyping`, `dataset`, `report`, and `agent_tool`.

### Metrics

| Metric | Meaning |
| --- | --- |
| `source_hit_at_k` | Whether top-k retrieved chunks contain an expected source file. |
| `keyword_recall` | Fraction of expected keywords found in retrieved chunks or answer text. |
| `citation_hit` | Whether citations point to expected sources. |
| `answer_point_coverage` | Fraction of expected answer points covered by the generated answer or retrieved context. |
| `retrieval_empty_rate` | Fraction of questions with no retrieved chunks. |
| `average_score` | Simple average of source hit, keyword recall, citation hit, and answer coverage. |

### CLI

```bash
python -m rag_eval.cli \
  --eval-file examples/eval/rag_eval_questions.jsonl \
  --docs-dir examples \
  --top-k 3 \
  --output-dir reports/rag_eval \
  --use-agent-answer false \
  --retriever auto \
  --rebuild-index true
```

The command writes:

- `reports/rag_eval/rag_eval_summary_*.json`
- `reports/rag_eval/rag_eval_details_*.json`
- `reports/rag_eval/rag_eval_report_*.md`

Sample public outputs are included under `examples/outputs/`.

### FastAPI

Start the backend:

```bash
uvicorn app.main:app --reload
```

Run evaluation:

```bash
curl -X POST http://localhost:8000/rag-eval/run ^
  -H "Content-Type: application/json" ^
  -d "{\"eval_file\":\"examples/eval/rag_eval_questions.jsonl\",\"docs_dir\":\"examples\",\"top_k\":3,\"use_agent_answer\":false,\"retriever\":\"auto\",\"rebuild_index\":true}"
```

Download generated artifacts:

- `GET /rag-eval/reports/{filename}`
- `GET /rag-eval/results/{filename}`

### Streamlit

Start the frontend:

```bash
streamlit run frontend/streamlit_app.py
```

Use the `RAG Evaluation` section to choose the eval file, top_k, retriever backend, and whether to call the Agent answer path. The UI displays summary metrics, metrics by category, low-score failure cases, and report downloads.

### How To Read The Report

- Low `source_hit_at_k`: check chunk splitting, source metadata, and top_k.
- Low `keyword_recall`: try query rewrite, stronger embeddings, or hybrid keyword + vector retrieval.
- Low `citation_hit`: inspect citation binding between retrieved chunks and source filenames.
- Low `answer_point_coverage`: improve prompt wording or pass more relevant context.
- High `retrieval_empty_rate`: inspect document loading and index rebuild behavior.

### Future Improvements

- Add real embedding providers and compare against the current hashing embeddings.
- Add reranking and hybrid search.
- Expand the eval set with more real failure modes and manually labeled expected sources.
- Add LLM-as-judge only after deterministic retrieval metrics are stable.
- Persist query, retrieval, citation, and report traces for regression tracking.

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
