# Free Setup Guide

## ✅ Everything is Now 100% Free!

Your project has been converted to use **completely free** services. No payment methods required (except AWS EC2 free tier, which won't charge you if you stay within limits).

## What Changed

### 1. LLM (ClassifierAgent) - ✅ FREE
- **Before**: OpenAI (requires payment method, costs money)
- **After**: Groq (free tier, no payment method needed)
- **Model**: `llama-3.1-8b-instant` (fast, free, good quality)
- **Limits**: 30 requests/minute (generous for free tier)

### 2. Embeddings (Vector DB) - ✅ FREE
- **Before**: OpenAI embeddings (costs money)
- **After**: HuggingFace sentence-transformers (free, runs locally)
- **Model**: `all-MiniLM-L6-v2` (fast, free, good quality)
- **Storage**: Local (no API calls needed)

### 3. Vector Database - ✅ FREE
- **ChromaDB**: Free (local storage, no cloud costs)

### 4. Cloud Deployment - ✅ FREE (EC2 Free Tier)
- **EC2 t2.micro/t3.micro**: 750 hours/month free
- **Enough for**: 24/7 operation on one instance
- **Note**: AWS account needed (free tier eligible)

## Setup Steps

### Step 1: Get Groq API Key (Free)

1. Go to: https://console.groq.com/
2. Sign up (no payment method required!)
3. Go to API Keys section
4. Create new API key
5. Copy it

### Step 2: Update .env File

Add to your `.env` file:
```
GROQ_API_KEY=your-groq-api-key-here
```

**Note**: You can remove `OPENAI_API_KEY` if you're not using OpenAI anymore.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `langchain-groq` (free LLM)
- `langchain-huggingface` (free embeddings)
- `sentence-transformers` (free embeddings)

### Step 4: Run Ingestion

```bash
python -m src.utils.ingest_policies
```

This creates embeddings for your policies (free, runs locally).

### Step 5: Test Locally

```bash
uvicorn src.api.main:app --reload
```

Visit: http://localhost:8000/docs

## Cost Breakdown

| Service | Cost | Payment Method Needed? |
|---------|------|----------------------|
| Groq API | $0 (free tier) | ❌ No |
| HuggingFace | $0 (free) | ❌ No |
| ChromaDB | $0 (local) | ❌ No |
| EC2 Free Tier | $0 (750 hrs/month) | ⚠️ Yes (but won't charge if within limits) |
| **Total** | **$0/month** | |

## Free Tier Limits

### Groq Free Tier
- **30 requests/minute**
- **Generous daily limits**
- **No payment method needed**

### AWS EC2 Free Tier
- **750 hours/month** (enough for 24/7)
- **t2.micro or t3.micro** instances
- **30 GB storage** (EBS)
- **Credit card required** (but won't charge if you stay within limits)

## Deployment to EC2

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete EC2 deployment guide.

## Testing

Test that everything works:

```bash
# Test ingestion
python -m src.utils.ingest_policies

# Test API
uvicorn src.api.main:app --reload

# Test endpoint (in another terminal)
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"id": "test1", "text": "Hello, how are you?"}'
```

## Troubleshooting

### "GROQ_API_KEY not found" error?
- Make sure `.env` file has `GROQ_API_KEY=your-key`
- Check that `load_dotenv()` is called in your code

### Out of memory on EC2?
- t2.micro has 1GB RAM (might be tight)
- Use t3.micro (2GB RAM) - still free tier eligible

### Groq rate limits?
- Free tier: 30 requests/minute
- If you need more, consider upgrading (but free tier is generous)

## Summary

✅ **Everything is FREE**
✅ **No payment methods needed** (except AWS, but won't charge)
✅ **Ready for EC2 deployment**
✅ **Production-ready** (with free tier limits)

Your project is now **100% free** and ready to deploy! 🚀

