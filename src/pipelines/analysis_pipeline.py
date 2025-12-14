from typing import Dict, Any

from ..agents.classifier_agent import ClassifierAgent


class AnalysisPipeline:
    """
    Orchestrates multiple agents to produce a final policy decision.
    """

    def __init__(self):
        self.classifier = ClassifierAgent()
        # TODO: add retriever_agent, compliance_agent

    async def analyze(self, content_id: str, text: str) -> Dict[str, Any]:
        """
        Main entry point for content analysis.
        Returns a dict shaped like AnalysisResponse.
        """
        # 1) classification
        cls_result = await self.classifier.run(text=text)

        if not cls_result["needs_review"]:
            decision = {
                "label": "allowed",
                "confidence": 0.8,
                "reasons": [
                    f"Classifier categorized as '{cls_result['category']}' and no review needed.",
                    cls_result["explanation"],
                ],
            }
        else:
            # TODO: use retriever + compliance agents here
            decision = {
                "label": "flag",
                "confidence": 0.6,
                "reasons": [
                    f"Classifier flagged category '{cls_result['category']}' requiring review.",
                    "Detailed compliance check pipeline not yet implemented.",
                ],
            }

        return {
            "content_id": content_id,
            "decision": decision,
        }
