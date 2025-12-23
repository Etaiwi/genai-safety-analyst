import os
from typing import Any, Dict, List, Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from .base import BaseAgent


class ComplianceResult(BaseModel):
    """Structured output for compliance agent"""
    label: Literal["allowed", "flag", "block"] = Field(description="Policy decision: 'allowed', 'flag', or 'block'")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    reasons: List[str] = Field(description="2-5 short bullet reasons for the decision")


class ComplianceAgent(BaseAgent):
    """
    Produces a final policy decision using the content + retrieved policies.
    Uses Groq for LLM inference.
    """

    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        # Obtain API key from https://console.groq.com/
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment. "
                "Obtain API key from https://console.groq.com/"
            )
        self.llm = ChatGroq(model=model_name, temperature=0.0, groq_api_key=api_key)
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are a policy compliance analyst for user-generated content.

            Content:
            {text}

            Classifier category:
            {category}

            Retrieved policy snippets:
            {policies}

            Task:
            Decide the best policy outcome:
              - allowed
              - flag
              - block

            Provide:
              - label: one of allowed/flag/block
              - confidence: number 0..1
              - reasons: 2-5 short bullet reasons tied to the policies when possible

            Respond in JSON with keys: label, confidence, reasons
            """
        )

    async def run(self, **kwargs) -> Dict[str, Any]:
        text: str = kwargs["text"]
        category: str = kwargs.get("category", "")
        policies_list: List[Dict[str, Any]] = kwargs.get("retrieved_policies", [])

        # Compact format for LLM input
        policies_str = "\n\n".join(
            [
                f"[{p.get('policy_id')}] {p.get('title')} (cat={p.get('category')}, severity={p.get('severity')})\n{p.get('snippet')}"
                for p in policies_list
            ]
        ) or "None"

        chain = self.prompt | self.llm.with_structured_output(ComplianceResult)
        result = await chain.ainvoke(
            {"text": text, "category": category, "policies": policies_str}
        )

        # Convert Pydantic model to dict (confidence already validated by Pydantic)
        return result.model_dump()

