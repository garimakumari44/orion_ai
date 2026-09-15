"""
Configuration models for Adaptive Retrieval.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AdaptiveRetrievalConfig(BaseModel):
    """
    Configuration controlling adaptive retrieval behaviour.
    """

    enabled: bool = True

    default_strategy: str = "hybrid"

    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    rerank_top_k: int = Field(
        default=50,
        ge=1,
        le=500,
    )

    similarity_threshold: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
    )

    enable_query_classification: bool = True

    enable_fallback: bool = True

    enable_reranking: bool = True

    enable_query_expansion: bool = True

    max_latency_ms: int = 3000