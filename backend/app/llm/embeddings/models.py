"""
Data models for the embedding subsystem.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """
    Request to generate an embedding.
    """

    text: str = Field(..., min_length=1)
    model: Optional[str] = None


class BatchEmbeddingRequest(BaseModel):
    """
    Request to generate embeddings for multiple texts.
    """

    texts: List[str] = Field(..., min_length=1)
    model: Optional[str] = None


class EmbeddingResponse(BaseModel):
    """
    Response containing a single embedding vector.
    """

    embedding: List[float]
    dimension: int
    model: str


class BatchEmbeddingResponse(BaseModel):
    """
    Response containing multiple embedding vectors.
    """

    embeddings: List[List[float]]
    dimension: int
    model: str


class CachedEmbedding(BaseModel):
    """
    Object stored in the embedding cache.
    """

    text: str
    model: str
    embedding: List[float]