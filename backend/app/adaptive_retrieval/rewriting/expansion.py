"""
Query Expansion

Expands a user query with synonyms, related concepts,
domain knowledge, and optional LLM-generated expansions.

This improves recall during retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


# ==========================================================
# Models
# ==========================================================

@dataclass(slots=True)
class ExpansionRequest:
    query: str
    max_expansions: int = 20


@dataclass(slots=True)
class ExpansionResult:
    original_query: str
    expanded_query: str
    expansion_terms: List[str] = field(default_factory=list)


# ==========================================================
# Query Expansion
# ==========================================================

class QueryExpander:

    DEFAULT_SYNONYMS: Dict[str, List[str]] = {
        "car": ["automobile", "vehicle"],
        "bike": ["bicycle", "cycle"],
        "llm": [
            "large language model",
            "foundation model",
            "language model",
        ],
        "rag": [
            "retrieval augmented generation",
            "retrieval augmentation",
        ],
        "gpu": [
            "graphics processing unit",
            "cuda",
        ],
        "nlp": [
            "natural language processing",
            "text processing",
        ],
        "database": [
            "db",
            "storage",
            "datastore",
        ],
        "vector": [
            "embedding",
            "dense representation",
        ],
        "search": [
            "retrieval",
            "lookup",
            "information retrieval",
        ],
    }

    def __init__(
        self,
        synonym_map: Dict[str, List[str]] | None = None,
    ) -> None:

        self.synonyms = synonym_map or self.DEFAULT_SYNONYMS

    # ------------------------------------------------------

    def expand(
        self,
        request: ExpansionRequest,
    ) -> ExpansionResult:

        query = request.query.strip()

        expansions: Set[str] = set()

        for token in query.lower().split():

            if token in self.synonyms:

                expansions.update(self.synonyms[token])

        expansion_terms = sorted(expansions)

        expansion_terms = expansion_terms[: request.max_expansions]

        expanded_query = query

        if expansion_terms:
            expanded_query += " " + " ".join(expansion_terms)

        return ExpansionResult(
            original_query=query,
            expanded_query=expanded_query,
            expansion_terms=expansion_terms,
        )