# Deployment Guide - AWS EC2

This guide covers deploying the GenAI Safety Analyst to AWS EC2 using free tier eligible instances.

## Prerequisites

1. AWS Account (free tier eligible)
2. Groq API Key
   - Sign up at: https://console.groq.com/
   - Obtain your API key

## Cost Structure

- EC2 t2.micro/t3.micro: 750 hours/month (free tier)
- Groq LLM API: Tier-based (30 requests/minute on free tier)
- HuggingFace Embeddings: Local execution (no API costs)
- ChromaDB: Local storage (no cloud costs)

## Step 1: Obtain Groq API Key

1. Visit https://console.groq.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key for environment configuration

## Step 2: Configure Environment Variables

Add to your `.env` file:
```
GROQ_API_KEY=your-groq-api-key-here
```

## Step 3: Launch EC2 Instance

1. Navigate to AWS Console → EC2
2. Launch Instance:
   - AMI: Amazon Linux 2023 (free tier eligible)
   - Instance Type: t2.micro or t3.micro (free tier)
   - Key Pair: Create/download a key pair for SSH
   - Security Group: 
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere (0.0.0.0/0)
     - Allow Custom TCP (port 8000) from anywhere (for FastAPI)

3. Launch the instance

## Step 4: Connect to EC2

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

## Step 5: Install Dependencies on EC2

```bash
# Update system
sudo yum update -y

# Install Python 3.11+
sudo yum install python3.11 python3.11-pip git -y

# Clone your repository (or upload files)
git clone your-repo-url
cd genai-safety-analyst

# Install Python dependencies
pip3.11 install -r requirements.txt

# Or if using virtual environment:
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 6: Set Up Environment Variables

```bash
# Create .env file
nano .env

# Add:
GROQ_API_KEY=your-groq-api-key-here

# Save and exit (Ctrl+X, Y, Enter)
```

## Step 7: Run Ingestion (One-Time Setup)

```bash
python3.11 -m src.utils.ingest_policies
```

Expected output: `Ingested 6 policy docs into Chroma.`

## Step 8: Start the API Server

### Option A: Direct Run (for testing)
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Option B: Run as Service (recommended for production)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/genai-safety.service
```

Add:
```ini
[Unit]
Description=GenAI Safety Analyst API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/genai-safety-analyst
Environment="PATH=/home/ec2-user/genai-safety-analyst/venv/bin"
ExecStart=/home/ec2-user/genai-safety-analyst/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable genai-safety
sudo systemctl start genai-safety
sudo systemctl status genai-safety
```

## Step 9: Access Your API

Your API will be available at:
- `http://your-ec2-public-ip:8000`
- Health check: `http://your-ec2-public-ip:8000/health`
- API docs: `http://your-ec2-public-ip:8000/docs`

## Step 10: (Optional) Set Up Domain Name

1. Obtain a domain (Freenom or Route 53)
2. Point DNS to your EC2 IP
3. Configure nginx as reverse proxy (optional)

## Monitoring & Maintenance

### Check logs:
```bash
sudo journalctl -u genai-safety -f
```

### Restart service:
```bash
sudo systemctl restart genai-safety
```

### Check disk space:
```bash
df -h
```

## Service Limits

- EC2: 750 hours/month (sufficient for continuous operation on one instance)
- Groq: 30 requests/minute (free tier)
- Storage: 30 GB free (EBS)

## Troubleshooting

### Port not accessible?
- Verify security group rules
- Check EC2 instance firewall configuration

### API key errors?
- Verify `.env` file contains `GROQ_API_KEY`
- Check Groq console for API key status

### Out of memory?
- t2.micro provides 1GB RAM (may be insufficient)
- Consider t3.micro (2GB RAM) - still free tier eligible

### Tests not running locally?
- Use `PYTHONPATH=. pytest -q` (required for src/ directory structure)

## Security Notes

1. Never commit `.env` to Git (already in `.gitignore`)
2. Use security groups to limit access
3. Keep EC2 updated: `sudo yum update -y`
4. Use HTTPS in production (configure Let's Encrypt)

## Testing After Deployment

Once deployed, test the application:

```bash
# Health check
curl http://your-ec2-ip:8000/health

# Test analysis endpoint
curl -X POST "http://your-ec2-ip:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"id": "test1", "text": "Hello, how are you?"}'
```

## Cost Monitoring

- Review AWS Billing Dashboard regularly
- Configure billing alerts
- Monitor EC2 usage in CloudWatch (free tier)

---

## Summary

The deployment uses:
- EC2 free tier (750 hrs/month)
- Groq tier-based LLM API
- HuggingFace local embeddings
- ChromaDB local storage

The architecture supports production deployment while maintaining low operational costs.
