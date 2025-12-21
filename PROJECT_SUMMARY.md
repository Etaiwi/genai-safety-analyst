# GenAI Safety Analyst - Project Summary

## Project Overview

A multi-agent content safety analysis system that uses RAG (Retrieval-Augmented Generation) to classify and evaluate user content against policy rules. Built with FastAPI, LangChain, Groq, and HuggingFace. The architecture is designed for cost efficiency using open-source and tier-based services.

## Architecture

### Multi-Agent Pipeline

```
User Content
    ↓
[ClassifierAgent] → Categorizes content (harassment, self-harm, benign, etc.)
    ↓
[RetrieverAgent] → Finds relevant policies using semantic search (RAG)
    ↓
[ComplianceAgent] → Makes final decision (allowed/flag/block)
    ↓
Policy Decision (label, confidence, reasons)
```

## Project Structure

```
genai-safety-analyst/
├── src/
│   ├── agents/
│   │   ├── base.py                 # Base agent abstract class
│   │   ├── classifier_agent.py     # Content categorization
│   │   ├── retriever_agent.py      # Policy retrieval (RAG)
│   │   └── compliance_agent.py     # Final decision maker
│   ├── api/
│   │   └── main.py                 # FastAPI REST API
│   ├── pipelines/
│   │   └── analysis_pipeline.py   # Orchestrates all agents
│   ├── utils/
│   │   ├── policy_loader.py        # Loads policies from CSV
│   │   ├── vector_db.py            # ChromaDB wrapper with HuggingFace embeddings
│   │   └── ingest_policies.py      # One-time ingestion script
│   └── data/
│       └── rules/
│           └── policies.csv        # Policy rules (6 categories)
├── storage/
│   └── chroma/                      # Vector database (generated)
├── requirements.txt                 # Python dependencies
├── README.md                        # Setup instructions
├── DEPLOYMENT.md                    # EC2 deployment guide
└── PROJECT_SUMMARY.md               # This file
```

## Components

### 1. Agents

#### BaseAgent (`src/agents/base.py`)
- Abstract base class for all agents
- Defines `async run(**kwargs)` interface
- Ensures consistent agent structure

#### ClassifierAgent (`src/agents/classifier_agent.py`)
- Purpose: Categorizes user content
- LLM: Groq (llama-3.1-8b-instant)
- Input: User text
- Output: `{category, needs_review, explanation}`

#### RetrieverAgent (`src/agents/retriever_agent.py`)
- Purpose: Finds relevant policies using semantic search
- Technology: RAG (Retrieval-Augmented Generation)
- Embeddings: HuggingFace (all-MiniLM-L6-v2)
- Vector DB: ChromaDB (local storage)
- Input: User text + category
- Output: `{retrieved_policies: [...]}`

#### ComplianceAgent (`src/agents/compliance_agent.py`)
- Purpose: Makes final policy decision
- LLM: Groq (llama-3.1-8b-instant)
- Input: User text + category + retrieved policies
- Output: `{label, confidence, reasons}`

### 2. Pipeline

#### AnalysisPipeline (`src/pipelines/analysis_pipeline.py`)
- Orchestrates all three agents
- Flow:
  1. ClassifierAgent → Get category
  2. If `needs_review=False` → Return "allowed"
  3. If `needs_review=True` → RetrieverAgent → ComplianceAgent → Return decision

### 3. Utilities

#### PolicyLoader (`src/utils/policy_loader.py`)
- Loads policies from CSV
- Converts to `PolicyDoc` dataclass
- Handles missing values

#### VectorStore (`src/utils/vector_db.py`)
- Wraps ChromaDB vector database
- Uses HuggingFace embeddings (local execution)
- Provides semantic search functionality
- Stores policies as embeddings for fast retrieval

#### IngestPolicies (`src/utils/ingest_policies.py`)
- One-time setup script
- Loads policies → Creates embeddings → Stores in ChromaDB
- Run once: `python -m src.utils.ingest_policies`

### 4. API

#### FastAPI (`src/api/main.py`)
- REST API with two endpoints:
  - `GET /health` - Health check
  - `POST /analyze` - Content analysis
- Request: `{id, text, language?}`
- Response: `{content_id, decision: {label, confidence, reasons}}`

### 5. Data

#### Policies CSV (`src/data/rules/policies.csv`)
- 6 policy categories:
  - harassment, self-harm, hate, sexual, benign, politics
- Columns: `id, category, title, text, severity`

## Cost Structure

| Component | Service | Cost Model |
|-----------|---------|------------|
| LLM | Groq | Tier-based (generous free tier available) |
| Embeddings | HuggingFace | Local execution (no API costs) |
| Vector DB | ChromaDB | Local storage (no cloud costs) |
| API Framework | FastAPI | Open source |
| Cloud (optional) | EC2 | Free tier eligible (750 hrs/month) |

## Complete Flow Example

```
1. User sends: "I'm going to hurt myself"
   ↓
2. ClassifierAgent:
   - Analyzes text
   - Returns: {category: "self-harm", needs_review: true}
   ↓
3. RetrieverAgent:
   - Searches vector DB for "self-harm" policies
   - Finds: Policy p2 (Self-harm, severity: high)
   - Returns: [{policy_id: "p2", title: "Self-harm", ...}]
   ↓
4. ComplianceAgent:
   - Analyzes content against retrieved policy
   - Decides: label="block", confidence=0.95
   - Reasons: ["Content describes self-harm intent", "Matches high-severity policy"]
   ↓
5. API Response:
   {
     "content_id": "user123",
     "decision": {
       "label": "block",
       "confidence": 0.95,
       "reasons": [...]
     }
   }
```

## Technology Stack

### Core
- Python 3.11+
- FastAPI - Web framework
- LangChain - LLM orchestration
- Pydantic - Data validation

### LLM & AI
- Groq - LLM API (llama-3.1-8b-instant)
- HuggingFace - Embeddings (sentence-transformers)
- ChromaDB - Vector database

### Utilities
- pandas - CSV processing
- python-dotenv - Environment variables
- uvicorn - ASGI server

## Key Features

- Multi-Agent Architecture - Three specialized agents working together
- RAG-Based Retrieval - Semantic search for policy matching
- Fast Inference - Optimized LLM inference via Groq
- Local Embeddings - No API calls required for embeddings
- Structured Output - Consistent JSON responses
- Production-Ready - Deployable to cloud infrastructure

## Environment Variables

Required:
- `GROQ_API_KEY` - Obtain from https://console.groq.com/

## Setup Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Obtain Groq API key: https://console.groq.com/
3. Create `.env`: `GROQ_API_KEY=your-key-here`
4. Ingest policies: `python -m src.utils.ingest_policies`
5. Run API: `uvicorn src.api.main:app --reload`

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Analyze content
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"id": "test1", "text": "Hello, how are you?"}'
```

## Deployment

See `DEPLOYMENT.md` for EC2 deployment instructions.

## Learning Points

This project demonstrates:
- Multi-agent systems - Specialized agents working together
- RAG (Retrieval-Augmented Generation) - Semantic search + LLM
- Vector databases - Embeddings and similarity search
- Cost-optimized AI services - Efficient service selection
- FastAPI - Modern Python web APIs
- LangChain - LLM orchestration patterns

## Future Enhancements

Potential improvements:
- Add more policy categories
- Support multiple languages
- Add caching for repeated queries
- Implement rate limiting
- Add monitoring/logging
- Support batch processing
- Add web UI
- Implement fine-tuning for specific domains

## Documentation Files

- `README.md` - Quick start guide
- `DEPLOYMENT.md` - EC2 deployment instructions
- `PROJECT_SUMMARY.md` - This overview

---

**Status**: Complete and ready for deployment
**License**: See LICENSE file
