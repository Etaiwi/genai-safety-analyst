# GenAI Safety Analyst

A production-style **GenAI service** that analyzes user-generated text for safety/compliance using an **agentic LLM pipeline** and **RAG (Retrieval-Augmented Generation)**.

It exposes:
- a minimal **Web UI** (`/`) for quick demos
- a **REST API** (`/analyze`)
- an **OpenAPI playground** (`/docs`)

---

## What it does

Given an input text, the system:
1. **ClassifierAgent (LLM)**: categorizes the content and decides whether deeper review is needed
2. **RetrieverAgent (RAG + Chroma)**: fetches relevant policy snippets using vector similarity search
3. **ComplianceAgent (LLM)**: outputs a final decision (`allowed`, `flag`, `block`) with confidence and reasons

---

## Architecture (high level)

```
UI / API  →  FastAPI  →  AnalysisPipeline
                         ├─ ClassifierAgent (LLM)
                         ├─ RetrieverAgent (RAG + Chroma)
                         └─ ComplianceAgent (LLM)
```

---

## Quickstart (Local)

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure env
Create `.env` (do not commit it). Use `.env.example` as a template.

### 3) Ingest policies (RAG index)
```bash
python -m src.utils.ingest_policies
```

### 4) Run
```bash
make run
```

Open:
- UI: http://localhost:8000/
- API docs: http://localhost:8000/docs

---

## API usage

Example request:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"id":"demo1","text":"I hate you and you should disappear."}'
```

---

## Evaluation (pandas + NumPy)

Run evaluation over sample inputs:
```bash
make eval
```

- Input: `src/eval/eval_samples.csv`
- Output: `src/eval/eval_results.csv` (generated)

---

## Tests

```bash
make test
```

Tests mock LLM calls to keep CI reliable and fast.

---

## Docker

Build & run locally:
```bash
make docker-build
make docker-run
```

---

## Deployment (Google Cloud Run)

This project is designed to be deployed to **Google Cloud Run** as a container.

See: `DEPLOYMENT.md`

---

## Skills demonstrated

- LLM-integrated services (FastAPI + LangChain-based agents)
- Agentic components (classifier → retriever → compliance)
- Prompt engineering with structured outputs
- RAG with vector DB (Chroma) and policy grounding
- Python for GenAI (async orchestration, modular codebase)
- pandas + NumPy (policy ingestion + evaluation harness)
- Docker + CI (GitHub Actions) + testing strategy
- Cloud deployment (Cloud Run)

---

## Notes

This project is intentionally scoped to demonstrate **production thinking** (architecture, reliability, clarity),
not to maximize model accuracy.
