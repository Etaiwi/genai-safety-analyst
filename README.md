# genai-safety-analyst

FastAPI service that runs a small agentic pipeline (LangChain + OpenAI) to classify content and return a structured safety decision.

## Run locally
```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload