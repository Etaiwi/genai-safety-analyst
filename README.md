# GenAI Safety Analyst

A small, production-style content safety service built with FastAPI, LangChain, Groq, Hugging Face embeddings, and ChromaDB.  
The service accepts free-text input and returns structured safety decisions (ALLOWED / FLAG / BLOCK) with categories, confidence scores, and reasoning.

---

## Overview

The application is designed as a modular microservice that can be used as a building block in content moderation and trust & safety pipelines.

Main capabilities:

- Accepts text via:
  - A minimal web UI (`/`)
  - A JSON API endpoint (`/analyze`, depending on routing configuration)
- Runs a multi-step analysis pipeline:
  - Classifies the content into a coarse safety category.
  - Retrieves relevant policy snippets using a vector database and embeddings.
  - Produces a final decision (ALLOWED / FLAG / BLOCK) with explanations.
- Applies basic guardrails:
  - Maximum input length.
  - Simple per-IP rate limiting.
  - Optional demo token for public-facing deployments.

---

## Live deployment

The service is deployed on Google Cloud Run and available at:

```text
https://genai-safety-analyst-385217468790.us-central1.run.app/
```

---

## Architecture

High-level flow:

1. Incoming text is validated and checked against guardrails.
2. `ClassifierAgent` uses a Groq-backed LLM to classify the text and determine whether detailed policy checks are required.
3. `RetrieverAgent` uses Hugging Face embeddings and ChromaDB to retrieve relevant policy records from a policy corpus.
4. `ComplianceAgent` combines the text and retrieved policies to generate a final decision and reasoning.
5. The response is returned as a structured JSON payload and optionally rendered in a simple HTML UI.

Code layout:

```text
src/
  api/
    main.py              # FastAPI application: routes, health, docs
    ui.py                # Simple HTML UI for manual testing
  agents/
    base.py
    classifier_agent.py
    retriever_agent.py
    compliance_agent.py
  pipelines/
    analysis_pipeline.py  # Orchestrates the agents end-to-end
  utils/
    guardrails.py         # Rate limiting, length checks, optional demo token
    policy_loader.py      # Load policies from CSV into internal objects
    vector_db.py          # Embeddings and ChromaDB integration
    ingest_policies.py    # CLI script to ingest policies into Chroma
  data/
    rules/policies.csv    # Policy corpus used by the retriever
tests/
  test_api.py
  test_pipeline.py
```

The application is intended to be run as a containerized microservice (Docker) and deployed to a managed environment such as Google Cloud Run.

---

## Technology Stack

- Python 3.11
- FastAPI and Uvicorn
- LangChain
- Groq chat completion models (`langchain_groq`)
- Hugging Face sentence-transformer embeddings (`langchain-huggingface`, `sentence-transformers`)
- ChromaDB (`langchain-chroma`)
- Docker
- GitHub Actions CI
- Ruff, Black, pytest, pre-commit

---

## Local Development

### Prerequisites

- Python 3.11
- Git
- Docker (optional but recommended for parity with deployment)
- A Groq API key
- A Hugging Face access token (recommended for reliable model downloads)

### Clone and set up a virtual environment

```bash
git clone https://github.com/<your-username>/genai-safety-analyst.git
cd genai-safety-analyst

python -m venv .venv
# Windows:
# .venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate
```

### Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration

The application uses environment variables for configuration.  
Create a `.env` file in the project root. An example:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Recommended
HF_TOKEN=your_huggingface_token_here

# Guardrails
MAX_TEXT_CHARS=1200
RATE_LIMIT_MAX_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60

# Optional: protect the web UI with a demo token header
# DEMO_TOKEN=some-secret-demo-token
```

The `.env` file is listed in `.gitignore` so that secrets are not committed.

---

## Ingesting Policies (RAG Setup)

Before using the full analysis pipeline, the policy corpus should be ingested into the local ChromaDB store.

From the project root with the virtual environment activated:

```bash
python -m src.utils.ingest_policies
```

This script:

- Reads `src/data/rules/policies.csv`.
- Converts each row into a policy document object.
- Creates text chunks and embeddings.
- Stores them in a ChromaDB collection under `./storage/chroma/`.

---

## Running the Application Locally

### Option A: Direct Uvicorn

```bash
uvicorn src.api.main:app --reload
```

By default, the service listens on:

- Web UI: `http://localhost:8000/`
- API docs (OpenAPI): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Option B: Docker

Build the Docker image:

```bash
docker build -t genai-safety-analyst:local .
```

Run the container with environment variables from `.env`:

```bash
docker run --rm   -p 8000:8000   --env-file .env   genai-safety-analyst:local
```

The service will again be available at `http://localhost:8000/`.

---

## Tests and Quality Checks

### Running tests

```bash
PYTHONPATH=. pytest -q
```

To run a specific test file:

```bash
PYTHONPATH=. pytest tests/test_api.py -v
```

### Pre-commit hooks

The repository is configured with pre-commit hooks for formatting and linting (Black, Ruff, etc.).

To install the hooks locally:

```bash
pre-commit install
```

To run all hooks explicitly:

```bash
pre-commit run --all-files
```

---

## Deployment

The project is designed to run as a containerized service.  
The recommended deployment target is Google Cloud Run with:

- Container image stored in Artifact Registry.
- Memory limit of at least 1 GiB to accommodate the embedding model.
- Environment variables supplied via Cloud Run configuration.

For a step-by-step Cloud Run deployment guide, see [`DEPLOYMENT.md`](./DEPLOYMENT.md).
