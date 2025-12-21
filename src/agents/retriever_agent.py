from typing import Any, Dict, List

from .base import BaseAgent
from ..utils.vector_db import VectorStore


class RetrieverAgent(BaseAgent):
    """
    Retrieves relevant policy snippets using vector similarity search (RAG).
    """

    def __init__(self, store: VectorStore | None = None, top_k: int = 4):
        self.store = store or VectorStore()
        self.top_k = top_k

    async def run(self, **kwargs) -> Dict[str, Any]:
        text: str = kwargs["text"]
        category: str = kwargs.get("category", "")

        # Query can be enriched with category to improve retrieval:
        query = f"Category: {category}\nContent: {text}" if category else text

        hits = self.store.similarity_search(
            query=query,
            k=self.top_k,
            category_filter=category if category else None,
        )

        retrieved: List[Dict[str, Any]] = []
        for doc, score in hits:
            retrieved.append(
                {
                    "policy_id": doc.metadata.get("policy_id"),
                    "title": doc.metadata.get("title"),
                    "category": doc.metadata.get("category"),
                    "severity": doc.metadata.get("severity"),
                    "snippet": doc.page_content,
                    "score": float(score),
                }
            )

        return {"retrieved_policies": retrieved}

