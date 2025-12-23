from unittest.mock import MagicMock

import pytest

from src.pipelines.analysis_pipeline import AnalysisPipeline


@pytest.mark.asyncio
async def test_pipeline_short_circuit_allowed(monkeypatch):
    # Create async mock functions
    async def fake_classifier_run(**kwargs):
        return {
            "category": "benign",
            "needs_review": False,
            "explanation": "Clearly harmless.",
        }

    # Mock the agent classes to avoid API key requirements
    mock_classifier = MagicMock()
    mock_classifier.run = fake_classifier_run

    # Patch the agent classes before AnalysisPipeline creates instances
    monkeypatch.setattr(
        "src.pipelines.analysis_pipeline.ClassifierAgent", MagicMock(return_value=mock_classifier)
    )
    monkeypatch.setattr("src.pipelines.analysis_pipeline.RetrieverAgent", MagicMock())
    monkeypatch.setattr("src.pipelines.analysis_pipeline.ComplianceAgent", MagicMock())

    pipeline = AnalysisPipeline()

    result = await pipeline.analyze(content_id="x1", text="hello world")
    assert result["content_id"] == "x1"
    assert result["decision"]["label"] == "allowed"
    assert result["decision"]["confidence"] >= 0.0
    assert len(result["decision"]["reasons"]) >= 1


@pytest.mark.asyncio
async def test_pipeline_full_flow_flag(monkeypatch):
    # Create async mock functions
    async def fake_classifier_run(**kwargs):
        return {
            "category": "harassment",
            "needs_review": True,
            "explanation": "Targeted insult.",
        }

    async def fake_retriever_run(**kwargs):
        return {
            "retrieved_policies": [
                {
                    "policy_id": "p1",
                    "title": "Harassment & Bullying",
                    "category": "harassment",
                    "severity": "medium",
                    "snippet": "Harassment policy snippet...",
                    "score": 0.12,
                }
            ]
        }

    async def fake_compliance_run(**kwargs):
        return {
            "label": "flag",
            "confidence": 0.8,
            "reasons": ["Matches harassment policy p1."],
        }

    # Mock all agent classes
    mock_classifier = MagicMock()
    mock_classifier.run = fake_classifier_run

    mock_retriever = MagicMock()
    mock_retriever.run = fake_retriever_run

    mock_compliance = MagicMock()
    mock_compliance.run = fake_compliance_run

    # Patch the agent classes before creating pipeline
    monkeypatch.setattr(
        "src.pipelines.analysis_pipeline.ClassifierAgent", MagicMock(return_value=mock_classifier)
    )
    monkeypatch.setattr(
        "src.pipelines.analysis_pipeline.RetrieverAgent", MagicMock(return_value=mock_retriever)
    )
    monkeypatch.setattr(
        "src.pipelines.analysis_pipeline.ComplianceAgent", MagicMock(return_value=mock_compliance)
    )

    pipeline = AnalysisPipeline()

    result = await pipeline.analyze(content_id="x2", text="you are disgusting")
    assert result["decision"]["label"] in ("allowed", "flag", "block")
    assert 0.0 <= result["decision"]["confidence"] <= 1.0
    assert isinstance(result["decision"]["reasons"], list)
    assert result["decision"]["label"] == "flag"
