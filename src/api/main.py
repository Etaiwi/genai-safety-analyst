from dotenv import load_dotenv

load_dotenv()  # loads GROQ_API_KEY for LLM service

from fastapi import FastAPI, Request
from pydantic import BaseModel

from functools import lru_cache
from src.pipelines.analysis_pipeline import AnalysisPipeline
from src.utils.guardrails import enforce_guardrails

from .ui import router as ui_router

app = FastAPI(
    title="GenAI Safety Analyst",
    description="LLM-powered multi-agent service for content safety analysis.",
    version="0.1.0",
)

app.include_router(ui_router)


@lru_cache(maxsize=1)
def get_pipeline() -> AnalysisPipeline:
    return AnalysisPipeline()


# === Request / Response Schemas ===


class ContentItem(BaseModel):
    id: str
    text: str
    language: str | None = "en"


class PolicyDecision(BaseModel):
    label: str  # e.g. "allowed", "flag", "block"
    confidence: float
    reasons: list[str]


class AnalysisResponse(BaseModel):
    content_id: str
    decision: PolicyDecision


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: Request, item: ContentItem):
    """
    Calls the async analysis pipeline with guardrails protection.
    """
    enforce_guardrails(request=request, text=item.text)
    pipeline = get_pipeline()
    result = await pipeline.analyze(content_id=item.id, text=item.text)
    return AnalysisResponse(
        content_id=result["content_id"], decision=PolicyDecision(**result["decision"])
    )
