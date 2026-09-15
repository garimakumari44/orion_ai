"""
Data models for the embedding subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmbeddingConfig:
    """
    Configuration for an embedding model.
    """

    provider: str
    model_name: str

    dimension: int

    batch_size: int = 32

    normalize: bool = True

    max_retries: int = 3

    timeout: float = 30.0


@dataclass(slots=True)
class EmbeddingResult:
    """
    Result of embedding one piece of text.
    """

    text: str

    embedding: list[float]