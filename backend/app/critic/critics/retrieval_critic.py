"""
Retrieval Critic.

Evaluates retrieval quality for RAG systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class RetrievalDocument:
    id: str
    score: float
    relevant: bool
    source: str


@dataclass
class RetrievalReport:
    retrieved: int
    relevant: int
    precision: float
    recall_estimate: float
    average_score: float
    issues: List[str]


class RetrievalCritic:

    def critique(
        self,
        documents: List[RetrievalDocument],
    ) -> RetrievalReport:

        if not documents:
            return RetrievalReport(
                retrieved=0,
                relevant=0,
                precision=0.0,
                recall_estimate=0.0,
                average_score=0.0,
                issues=["No documents retrieved."],
            )

        relevant = sum(doc.relevant for doc in documents)

        precision = relevant / len(documents)

        avg_score = sum(doc.score for doc in documents) / len(documents)

        issues = []

        if precision < 0.5:
            issues.append("Low retrieval precision.")

        if avg_score < 0.5:
            issues.append("Weak retrieval confidence.")

        if relevant == 0:
            issues.append("No relevant evidence found.")

        recall = min(1.0, relevant / 5)

        return RetrievalReport(
            retrieved=len(documents),
            relevant=relevant,
            precision=precision,
            recall_estimate=recall,
            average_score=avg_score,
            issues=issues,
        )