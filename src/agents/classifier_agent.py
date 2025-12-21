import os
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from .base import BaseAgent


class ClassifierResult(BaseModel):
    """Structured output for classifier agent"""
    category: str = Field(description="Content category (e.g. 'harassment', 'self-harm', 'politics', 'benign')")
    needs_review: bool = Field(description="Whether content requires detailed safety/compliance review")
    explanation: str = Field(description="Brief explanation of the classification")


class ClassifierAgent(BaseAgent):
    """
    Classifies incoming content into high-level categories and
    decides whether deeper safety checks are needed.
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
            You are a content safety classifier.

            Input text:
            {text}

            1. Classify the main category of this text
               (e.g. 'harassment', 'self-harm', 'politics', 'benign', etc.).
            2. Decide if this text requires a detailed safety/compliance review.
               Use true (boolean) if review is needed, false (boolean) if not.
            3. Explain briefly why.

            IMPORTANT: needs_review must be a boolean (true or false), not a string.
            """
        )

    async def run(self, **kwargs) -> Dict[str, Any]:
        text = kwargs["text"]
        chain = self.prompt | self.llm.with_structured_output(ClassifierResult)
        result = await chain.ainvoke({"text": text})
        # Convert Pydantic model to dict
        return result.model_dump()
