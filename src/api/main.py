from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from dotenv import load_dotenv
import os

from src.pipelines.analysis_pipeline import AnalysisPipeline

load_dotenv()  # loads OPENAI_API_KEY, etc.

app = FastAPI(
    title="GenAI Safety Analyst",
    description="LLM-powered multi-agent service for content safety analysis.",
    version="0.1.0",
)

pipeline = AnalysisPipeline()

# === Request / Response Schemas ===

class ContentItem(BaseModel):
    id: str
    text: str
    language: Optional[str] = "en"


class PolicyDecision(BaseModel):
    label: str               # e.g. "allowed", "flag", "block"
    confidence: float
    reasons: List[str]


class AnalysisResponse(BaseModel):
    content_id: str
    decision: PolicyDecision


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(item: ContentItem):
    """
    Calls the async analysis pipeline.
    """
    result = await pipeline.analyze(content_id=item.id, text=item.text)
    return AnalysisResponse(
        content_id=result["content_id"],
        decision=PolicyDecision(**result["decision"])
    )