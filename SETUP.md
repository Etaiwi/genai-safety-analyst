# Setup Guide

This guide covers the setup process for the GenAI Safety Analyst, including service configuration and deployment options.

## Architecture Overview

The system uses a cost-optimized architecture:

### 1. LLM (ClassifierAgent)
- Service: Groq
- Model: `llama-3.1-8b-instant`
- Configuration: Tier-based access (generous free tier available)
- Rate Limits: 30 requests/minute on free tier

### 2. Embeddings (Vector DB)
- Service: HuggingFace sentence-transformers
- Model: `all-MiniLM-L6-v2`
- Execution: Local (no API calls required)
- Storage: Local filesystem

### 3. Vector Database
- Service: ChromaDB
- Storage: Local filesystem
- No cloud costs

### 4. Cloud Deployment (Optional)
- Service: AWS EC2
- Instance Types: t2.micro or t3.micro (free tier eligible)
- Free Tier: 750 hours/month
- Note: AWS account required (free tier eligible)

## Setup Steps

### Step 1: Obtain Groq API Key

1. Visit: https://console.groq.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key for use in environment configuration

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your-groq-api-key-here
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `langchain-groq` - Groq LLM integration
- `langchain-huggingface` - HuggingFace embeddings
- `sentence-transformers` - Embedding models
- Other required dependencies

### Step 4: Initialize Vector Database

```bash
python -m src.utils.ingest_policies
```

This creates embeddings for your policies and stores them in ChromaDB. The process runs locally and does not require API calls.

### Step 5: Test Locally

```bash
uvicorn src.api.main:app --reload
```

The API will be available at: http://localhost:8000/docs

## Cost Structure

| Service | Cost Model | Notes |
|---------|------------|-------|
| Groq API | Tier-based | Free tier: 30 requests/minute |
| HuggingFace | Local execution | No API costs |
| ChromaDB | Local storage | No cloud costs |
| EC2 Free Tier | Tier-based | 750 hrs/month (if deployed) |

## Service Limits

### Groq Free Tier
- 30 requests/minute
- Daily limits apply
- No payment method required for free tier

### AWS EC2 Free Tier
- 750 hours/month (sufficient for continuous operation)
- t2.micro or t3.micro instances
- 30 GB storage (EBS)
- Credit card may be required but no charges if within limits

## Deployment to EC2

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete EC2 deployment instructions.

## Testing

Verify the installation:

```bash
# Test ingestion
python -m src.utils.ingest_policies

# Test API
uvicorn src.api.main:app --reload

# Test endpoint
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"id": "test1", "text": "Hello, how are you?"}'
```

## Troubleshooting

### "GROQ_API_KEY not found" error
- Verify `.env` file contains `GROQ_API_KEY=your-key`
- Ensure `load_dotenv()` is called in application code

### Out of memory on EC2
- t2.micro provides 1GB RAM (may be insufficient)
- Consider t3.micro (2GB RAM) - still free tier eligible

### Groq rate limits
- Free tier: 30 requests/minute
- Monitor usage in Groq console
- Consider tier upgrade if limits are exceeded

## Summary

The system is designed for cost efficiency using:
- Tier-based LLM services (Groq)
- Local embedding execution (HuggingFace)
- Local vector storage (ChromaDB)
- Optional cloud deployment (EC2 free tier)

The architecture supports production deployment while maintaining low operational costs.
