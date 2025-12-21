from dataclasses import dataclass
from typing import List
import pandas as pd


@dataclass
class PolicyDoc:
    doc_id: str
    category: str
    title: str
    text: str
    severity: str


def load_policies_csv(path: str) -> List[PolicyDoc]:
    df = pd.read_csv(path)
    df = df.fillna("")
    policies: List[PolicyDoc] = []
    for _, row in df.iterrows():
        policies.append(
            PolicyDoc(
                doc_id=str(row["id"]),
                category=str(row["category"]),
                title=str(row["title"]),
                text=str(row["text"]),
                severity=str(row.get("severity", "")),
            )
        )
    return policies
