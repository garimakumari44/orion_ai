"""
Constants used throughout the adaptive retrieval system.
"""

from __future__ import annotations


class RetrievalConstants:
    """
    Central constants registry for Adaptive Retrieval System.
    """

    # ============================================================
    # Retrieval Strategies
    # ============================================================

    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    GRAPH = "graph"
    TEMPORAL = "temporal"
    METADATA = "metadata"

    SUPPORTED_RETRIEVAL_STRATEGIES = {
        VECTOR,
        KEYWORD,
        HYBRID,
        GRAPH,
        TEMPORAL,
        METADATA,
    }


    # ============================================================
    # Default Limits
    # ============================================================

    DEFAULT_TOP_K = 10

    DEFAULT_RERANK_K = 50

    DEFAULT_MIN_SCORE = 0.25


    # ============================================================
    # Confidence Thresholds
    # ============================================================

    LOW_CONFIDENCE = 0.35

    MEDIUM_CONFIDENCE = 0.60

    HIGH_CONFIDENCE = 0.80


    # ============================================================
    # Query Types
    # ============================================================

    FACTUAL = "factual"

    SEMANTIC = "semantic"

    MULTIHOP = "multi_hop"

    TEMPORAL_QUERY = "temporal"

    ENTITY = "entity"


    SUPPORTED_QUERY_TYPES = {
        FACTUAL,
        SEMANTIC,
        MULTIHOP,
        TEMPORAL_QUERY,
        ENTITY,
    }


    # ============================================================
    # Ranking
    # ============================================================

    DEFAULT_VECTOR_WEIGHT = 0.5

    DEFAULT_KEYWORD_WEIGHT = 0.3

    DEFAULT_METADATA_WEIGHT = 0.2


    # ============================================================
    # Cache
    # ============================================================

    DEFAULT_CACHE_TTL = 3600

    MAX_CACHE_SIZE = 10000


    # ============================================================
    # Context Building
    # ============================================================

    DEFAULT_CONTEXT_WINDOW = 4096

    MAX_CONTEXT_CHUNKS = 20