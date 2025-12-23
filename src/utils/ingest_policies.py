from pathlib import Path

from dotenv import load_dotenv

from .policy_loader import load_policies_csv
from .vector_db import VectorStore, build_documents

load_dotenv()  # Load environment variables (GROQ_API_KEY not needed for embeddings)


def ingest():
    csv_path = Path("src/data/rules/policies.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing policies file: {csv_path}")

    policies = load_policies_csv(str(csv_path))
    docs = build_documents(policies)

    store = VectorStore()
    n = store.upsert_documents(docs)
    print(f"Ingested {n} policy docs into Chroma.")


if __name__ == "__main__":
    ingest()
