# GenAI Safety Analyst - Project Summary

## 🎯 Project Overview

A **100% free** multi-agent content safety analysis system that uses RAG (Retrieval-Augmented Generation) to classify and evaluate user content against policy rules. Built with FastAPI, LangChain, Groq (free LLM), and HuggingFace (free embeddings).

## 🏗️ Architecture

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

## 📁 Project Structure

```
genai-safety-analyst/
├── src/
│   ├── agents/
│   │   ├── base.py                 # Base agent abstract class
│   │   ├── classifier_agent.py     # Content categorization (Groq LLM)
│   │   ├── retriever_agent.py      # Policy retrieval (RAG)
│   │   └── compliance_agent.py     # Final decision maker (Groq LLM)
│   ├── api/
│   │   └── main.py                 # FastAPI REST API
│   ├── pipelines/
│   │   └── analysis_pipeline.py   # Orchestrates all agents
│   ├── utils/
│   │   ├── policy_loader.py        # Loads policies from CSV
│   │   ├── vector_db.py            # ChromaDB wrapper (HuggingFace embeddings)
│   │   └── ingest_policies.py      # One-time ingestion script
│   └── data/
│       └── rules/
│           └── policies.csv        # Policy rules (6 categories)
├── storage/
│   └── chroma/                      # Vector database (generated)
├── requirements.txt                 # Python dependencies
├── README.md                        # Setup instructions
├── DEPLOYMENT.md                    # EC2 deployment guide
├── FREE_SETUP.md                    # Free setup guide
└── PROJECT_SUMMARY.md               # This file
```

## 🔧 Components Explained

### 1. Agents

#### BaseAgent (`src/agents/base.py`)
- Abstract base class for all agents
- Defines `async run(**kwargs)` interface
- Ensures consistent agent structure

#### ClassifierAgent (`src/agents/classifier_agent.py`)
- **Purpose**: Categorizes user content
- **LLM**: Groq (llama-3.1-8b-instant) - FREE
- **Input**: User text
- **Output**: `{category, needs_review, explanation}`
- **Cost**: $0 (free tier)

#### RetrieverAgent (`src/agents/retriever_agent.py`)
- **Purpose**: Finds relevant policies using semantic search
- **Technology**: RAG (Retrieval-Augmented Generation)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2) - FREE
- **Vector DB**: ChromaDB (local storage)
- **Input**: User text + category
- **Output**: `{retrieved_policies: [...]}`
- **Cost**: $0 (runs locally)

#### ComplianceAgent (`src/agents/compliance_agent.py`)
- **Purpose**: Makes final policy decision
- **LLM**: Groq (llama-3.1-8b-instant) - FREE
- **Input**: User text + category + retrieved policies
- **Output**: `{label, confidence, reasons}`
- **Cost**: $0 (free tier)

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
- Uses HuggingFace embeddings (free, local)
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

## 💰 Cost Breakdown (100% Free!)

| Component | Service | Cost | Payment Needed? |
|-----------|---------|------|-----------------|
| LLM | Groq (free tier) | $0 | ❌ No |
| Embeddings | HuggingFace (local) | $0 | ❌ No |
| Vector DB | ChromaDB (local) | $0 | ❌ No |
| API Framework | FastAPI (open source) | $0 | ❌ No |
| Cloud (optional) | EC2 Free Tier | $0 | ⚠️ Yes* |

*AWS EC2 free tier requires account but won't charge if within limits (750 hrs/month)

## 🔄 Complete Flow Example

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

## 🚀 Technology Stack

### Core
- **Python 3.11+**
- **FastAPI** - Modern web framework
- **LangChain** - LLM orchestration
- **Pydantic** - Data validation

### LLM & AI
- **Groq** - Free LLM API (llama-3.1-8b-instant)
- **HuggingFace** - Free embeddings (sentence-transformers)
- **ChromaDB** - Vector database

### Utilities
- **pandas** - CSV processing
- **python-dotenv** - Environment variables
- **uvicorn** - ASGI server

## 📊 Key Features

✅ **100% Free** - No payment methods needed (except optional EC2)
✅ **Multi-Agent** - Three specialized agents working together
✅ **RAG-Based** - Semantic search for policy matching
✅ **Fast** - Groq provides very fast inference
✅ **Local Embeddings** - No API calls for embeddings
✅ **Structured Output** - Consistent JSON responses
✅ **Production-Ready** - Can deploy to EC2 free tier

## 🔐 Environment Variables

Required:
- `GROQ_API_KEY` - Get free key from https://console.groq.com/

Optional:
- None! Everything else runs locally or uses free services.

## 📝 Setup Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Get Groq API key**: https://console.groq.com/ (free, no payment)
3. **Create `.env`**: `GROQ_API_KEY=your-key-here`
4. **Ingest policies**: `python -m src.utils.ingest_policies`
5. **Run API**: `uvicorn src.api.main:app --reload`

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Analyze content
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"id": "test1", "text": "Hello, how are you?"}'
```

## 📦 Deployment

See `DEPLOYMENT.md` for complete EC2 free tier deployment guide.

## 🎓 Learning Points

This project demonstrates:
- **Multi-agent systems** - Specialized agents working together
- **RAG (Retrieval-Augmented Generation)** - Semantic search + LLM
- **Vector databases** - Embeddings and similarity search
- **Free AI services** - Building without costs
- **FastAPI** - Modern Python web APIs
- **LangChain** - LLM orchestration patterns

## 🔮 Future Enhancements

Potential improvements:
- [ ] Add more policy categories
- [ ] Support multiple languages
- [ ] Add caching for repeated queries
- [ ] Implement rate limiting
- [ ] Add monitoring/logging
- [ ] Support batch processing
- [ ] Add web UI
- [ ] Implement fine-tuning for specific domains

## 📚 Documentation Files

- `README.md` - Quick start guide
- `DEPLOYMENT.md` - EC2 deployment instructions
- `FREE_SETUP.md` - Free setup details
- `PROJECT_SUMMARY.md` - This comprehensive overview

---

**Status**: ✅ Complete and ready for deployment
**Cost**: 💰 $0/month (100% free)
**License**: See LICENSE file

