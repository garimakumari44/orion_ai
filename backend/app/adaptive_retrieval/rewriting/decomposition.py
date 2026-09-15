"""
Query Decomposition

Breaks complex user questions into
smaller retrieval-friendly subqueries.

Example
-------

Input:
    Compare GPT-4 and Claude and explain their pricing.

Output:
[
    "Compare GPT-4 and Claude",
    "Explain GPT-4 pricing",
    "Explain Claude pricing"
]
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

@dataclass
class DecompositionRequest:
    query: str


@dataclass
class DecompositionResult:
    original_query: str
    subqueries: List[str] = field(default_factory=list)
    is_complex: bool = False


# ---------------------------------------------------------
# Decomposer
# ---------------------------------------------------------

class QueryDecomposer:

    SPLIT_KEYWORDS = [
        " and ",
        " then ",
        " also ",
        " after ",
        " before ",
        ",",
    ]

    def decompose(
        self,
        request: DecompositionRequest,
    ) -> DecompositionResult:

        query = request.query.strip()

        subqueries = self._split(query)

        is_complex = len(subqueries) > 1

        subqueries = self._normalize(subqueries)

        return DecompositionResult(
            original_query=query,
            subqueries=subqueries,
            is_complex=is_complex,
        )

    # -----------------------------------------------------

    def _split(self, query: str) -> List[str]:

        pattern = "|".join(
            map(re.escape, self.SPLIT_KEYWORDS)
        )

        parts = re.split(pattern, query)

        cleaned = []

        for part in parts:

            part = part.strip()

            if part:
                cleaned.append(part)

        return cleaned

    # -----------------------------------------------------

    def _normalize(
        self,
        queries: List[str],
    ) -> List[str]:

        normalized = []

        for q in queries:

            q = re.sub(r"\s+", " ", q)

            if q.endswith("?"):
                q = q[:-1]

            normalized.append(q.strip())

        return normalized