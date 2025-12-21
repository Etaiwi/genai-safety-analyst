# genai-safety-analyst

FastAPI service that runs a multi-agent pipeline (LangChain + Groq + HuggingFace) to classify content and return structured safety decisions. **100% Free** - no payment methods required!

## Features

- ✅ **Free LLM**: Groq API (free tier, no payment needed)
- ✅ **Free Embeddings**: HuggingFace sentence-transformers (runs locally)
- ✅ **Free Vector DB**: ChromaDB (local storage)
- ✅ **Multi-Agent Pipeline**: Classifier → Retriever → Compliance agents
- ✅ **RAG-based**: Semantic search for policy matching

## Setup

### 1. Get Free API Key

**Groq API Key** (free, no payment method needed):
1. Sign up at: https://console.groq.com/
2. Get your free API key
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

## Deploy to AWS EC2 (Free Tier)

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide to deploy on AWS EC2 free tier.

## Cost: $0/month

- **Groq LLM**: Free tier (30 req/min)
- **HuggingFace**: Free (local embeddings)
- **ChromaDB**: Free (local storage)
- **EC2**: Free tier (750 hrs/month) - enough for 24/7