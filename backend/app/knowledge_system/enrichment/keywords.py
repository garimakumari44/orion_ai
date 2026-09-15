"""
Keyword extraction models.

Stores keywords and key phrases extracted from documents
for search, indexing, and retrieval.
"""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class Keyword(BaseModel):
    """
    Represents a single keyword or key phrase.
    """

    text: str = Field(..., description="Keyword or phrase")

    score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Importance score",
    )

    occurrences: int = Field(
        default=1,
        ge=1,
        description="Number of occurrences",
    )

    metadata: Dict[str, str] = Field(default_factory=dict)


class KeywordCollection(BaseModel):
    """
    Collection of extracted keywords.
    """

    keywords: List[Keyword] = Field(default_factory=list)

    def add(self, keyword: Keyword) -> None:
        self.keywords.append(keyword)

    def extend(self, keywords: List[Keyword]) -> None:
        self.keywords.extend(keywords)

    def top(self, limit: int = 10) -> List[Keyword]:
        return sorted(
            self.keywords,
            key=lambda k: k.score,
            reverse=True,
        )[:limit]