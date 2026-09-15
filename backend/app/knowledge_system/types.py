"""
Shared types for Knowledge System.

These models are used by:
- adaptive_retrieval
- agents
- orchestration
- API layers

This file contains shared contracts, not implementation logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional



# ============================================================
# Retrieval Strategy
# ============================================================

class RetrievalStrategy(str, Enum):
    """
    Available retrieval approaches.
    """

    VECTOR = "vector"
    KEYWORD = "keyword"
    BM25 = "bm25"
    HYBRID = "hybrid"
    GRAPH = "graph"
    MEMORY = "memory"
    METADATA = "metadata"



# ============================================================
# Retrieval Request
# ============================================================

@dataclass
class RetrievalRequest:
    """
    Input request sent to retrieval system.
    """

    query: str

    strategy: RetrievalStrategy = (
        RetrievalStrategy.HYBRID
    )

    top_k: int = 5

    filters: Optional[Dict[str, Any]] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )



# ============================================================
# Retrieved Document
# ============================================================

@dataclass
class RetrievedDocument:
    """
    A single retrieval result.

    Can wrap:
    - Chunk
    - Document
    - Memory item
    - Graph entity
    """

    document: Any

    score: float = 0.0

    source: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )



# ============================================================
# Retrieval Response
# ============================================================

@dataclass
class RetrievalResponse:
    """
    Output returned by retrieval pipeline.
    """

    query: str

    documents: List[RetrievedDocument]

    strategy: RetrievalStrategy

    total_results: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )



# ============================================================
# Exports
# ============================================================

__all__ = [
    "RetrievalStrategy",
    "RetrievalRequest",
    "RetrievedDocument",
    "RetrievalResponse",
]