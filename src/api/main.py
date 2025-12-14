from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from dotenv import load_dotenv
import os

load_dotenv()  # loads OPENAI_API_KEY, etc.

app = FastAPI(
    title="GenAI Safety Analyst",
    description="LLM-powered multi-agent service for content safety analysis.",
    version="0.1.0",
)

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
def analyze_content(item: ContentItem):
    """
    Placeholder implementation: will call our agentic pipeline later.
    """
    # TODO: replace this mock with real pipeline call
    dummy_decision = PolicyDecision(
        label="allowed",
        confidence=0.5,
        reasons=["Default placeholder decision. Pipeline not wired yet."]
    )
    return AnalysisResponse(
        content_id=item.id,
        decision=dummy_decision
    )
