"""
Query Router

Routes retrieval requests to appropriate
retrieval strategies based on query characteristics.

Responsibilities:
- Decide retrieval mode
- Select retrievers
- Coordinate retrieval path
"""


from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class QueryRoute(str, Enum):
    """
    Available retrieval routes.
    """

    VECTOR = "vector"

    KEYWORD = "keyword"

    HYBRID = "hybrid"

    GRAPH = "graph"

    MEMORY = "memory"

    MULTI_SOURCE = "multi_source"



@dataclass
class QueryRouter:
    """
    Determines retrieval strategy.

    Example:

    Simple factual query
        -> VECTOR

    Exact keyword query
        -> KEYWORD

    Complex research query
        -> HYBRID + GRAPH
    """


    def route(
        self,
        query: str,
        complexity: str | None = None
    ) -> List[QueryRoute]:

        query_lower = query.lower()


        # --------------------------------------------------
        # Keyword style queries
        # --------------------------------------------------

        if any(
            word in query_lower
            for word in [
                "exact",
                "definition",
                "name",
                "code"
            ]
        ):
            return [
                QueryRoute.KEYWORD
            ]


        # --------------------------------------------------
        # Complex research queries
        # --------------------------------------------------

        if complexity in (
            "high",
            "complex"
        ):
            return [
                QueryRoute.HYBRID,
                QueryRoute.GRAPH,
                QueryRoute.MEMORY
            ]


        # --------------------------------------------------
        # Default
        # --------------------------------------------------

        return [
            QueryRoute.VECTOR
        ]