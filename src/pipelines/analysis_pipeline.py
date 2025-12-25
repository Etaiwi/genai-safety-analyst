from typing import Any

from ..agents.classifier_agent import ClassifierAgent
from ..agents.compliance_agent import ComplianceAgent
from ..agents.retriever_agent import RetrieverAgent


class AnalysisPipeline:
    """
    Orchestrates multiple agents to produce a final policy decision.
    """

    def __init__(self):
        self.classifier = ClassifierAgent()
        self.retriever = RetrieverAgent()
        self.compliance = ComplianceAgent()

    async def analyze(self, content_id: str, text: str) -> dict[str, Any]:
        """
        Main entry point for content analysis.
        Returns a dict shaped like AnalysisResponse.
        """
        # 1) classification
        cls_result = await self.classifier.run(text=text)
        category = cls_result["category"]
        needs_review = cls_result["needs_review"]

        # If classifier says no review needed, still allow but with good reasons:
        if not needs_review:
            decision = {
                "label": "allowed",
                "confidence": 0.85,
                "category": category,
                "reasons": [
                    f"Classifier categorized as '{category}' and determined no further review is needed.",
                    cls_result["explanation"],
                ],
            }
            return {"content_id": content_id, "decision": decision}

        # 2) retrieval (RAG)
        retrieval = await self.retriever.run(text=text, category=category)
        retrieved_policies = retrieval["retrieved_policies"]

        # 3) compliance decision
        compliance = await self.compliance.run(
            text=text,
            category=category,
            retrieved_policies=retrieved_policies,
        )

        decision = {
            "label": compliance["label"],
            "confidence": compliance["confidence"],
            "category": category,
            "reasons": compliance["reasons"],
        }

        return {"content_id": content_id, "decision": decision}
