"""
Exceptions for the embedding service.
"""

from __future__ import annotations


class EmbeddingServiceError(Exception):
    """Base exception for embedding service."""


class EmbeddingProviderNotFoundError(EmbeddingServiceError):
    """Requested embedding provider is not registered."""


class EmbeddingGenerationError(EmbeddingServiceError):
    """Embedding generation failed."""