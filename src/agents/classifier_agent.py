from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .base import BaseAgent


class ClassifierAgent(BaseAgent):
    """
    Classifies incoming content into high-level categories and
    decides whether deeper safety checks are needed.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.0)
        self.prompt = ChatPromptTemplate.from_template(
            """
            You are a content safety classifier.

            Input text:
            {text}

            1. Classify the main category of this text
               (e.g. 'harassment', 'self-harm', 'politics', 'benign', etc.).
            2. Decide if this text requires a detailed safety/compliance review (yes/no).
            3. Explain briefly why.

            Respond in JSON with keys:
              - category: string
              - needs_review: boolean
              - explanation: string
            """
        )

    async def run(self, **kwargs) -> Dict[str, Any]:
        text = kwargs["text"]
        chain = self.prompt | self.llm.with_structured_output(
            schema={"type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "needs_review": {"type": "boolean"},
                        "explanation": {"type": "string"},
                    },
                    "required": ["category", "needs_review", "explanation"]}
        )
        result = await chain.ainvoke({"text": text})
        # result is already a parsed dict due to structured_output
        return result
