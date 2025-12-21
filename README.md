# genai-safety-analyst

FastAPI service that runs a multi-agent pipeline (LangChain + Groq + HuggingFace) to classify content and return structured safety decisions. The architecture is optimized for cost efficiency using open-source and tier-based services.

## Features

- Multi-Agent Pipeline: Classifier → Retriever → Compliance agents
- RAG-based Retrieval: Semantic search for policy matching
- Cost-Optimized: Uses tier-based services and local execution where possible
- Fast Inference: Optimized LLM inference via Groq
- Local Embeddings: HuggingFace sentence-transformers (runs locally)

## Setup

### 1. Obtain API Key

**Groq API Key**:
1. Sign up at: https://console.groq.com/
2. Obtain your API key
3. Add to `.env` file:

```bash
GROQ_API_KEY=your-groq-api-key-here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Ingest Policies (One-Time Setup)

```bash
python -m src.utils.ingest_policies
```

This creates the vector database with policy embeddings.

### 4. Run Locally

```bash
uvicorn src.api.main:app --reload
```

API will be available at: http://localhost:8000

- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Deploy to AWS EC2

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide to deploy on AWS EC2.

## Cost Structure

- **Groq LLM**: Tier-based (generous free tier available)
- **HuggingFace**: Local execution (no API costs)
- **ChromaDB**: Local storage (no cloud costs)
- **EC2**: Free tier eligible (750 hrs/month)
