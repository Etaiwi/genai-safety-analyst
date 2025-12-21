import os
from typing import List, Optional, Tuple

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma  # requires langchain-chroma package

from .policy_loader import PolicyDoc


def build_documents(policies: List[PolicyDoc]) -> List[Document]:
    docs: List[Document] = []
    for p in policies:
        docs.append(
            Document(
                page_content=f"{p.title}\n{p.text}",
                metadata={
                    "policy_id": p.doc_id,
                    "category": p.category,
                    "severity": p.severity,
                    "title": p.title,
                },
            )
        )
    return docs


class VectorStore:
    """
    Wrapper around Chroma vector store.
    """

    def __init__(
        self,
        persist_dir: str = "storage/chroma",
        collection_name: str = "policies",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        # Using free HuggingFace embeddings - no API key needed!
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},  # Use CPU (or "cuda" if you have GPU)
        )

        os.makedirs(self.persist_dir, exist_ok=True)
        self.vdb = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir,
        )

    def upsert_documents(self, docs: List[Document]) -> int:
        """
        Adds documents to the collection. Returns number of docs added.
        """
        # Chroma will store docs; duplicates can happen if you re-run.
        # For MVP, keep it simple; later we can implement deterministic IDs.
        self.vdb.add_documents(docs)
        return len(docs)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        category_filter: Optional[str] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Returns list of (Document, score). Lower score not always better depending on backend,
        but in practice this works fine for ranking with Chroma.
        """
        flt = None
        if category_filter:
            flt = {"category": category_filter}

        results = self.vdb.similarity_search_with_score(query, k=k, filter=flt)
        return results
