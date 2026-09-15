"""
Factory for embedding providers.
"""

from __future__ import annotations

from typing import Callable

from .base import BaseEmbeddingModel
from .models import EmbeddingConfig


class EmbeddingFactory:
    """
    Creates embedding model instances.

    Providers register themselves with the factory.
    """

    def __init__(self) -> None:
        self._builders: dict[
            str,
            Callable[[EmbeddingConfig], BaseEmbeddingModel],
        ] = {}

    def register(
        self,
        provider: str,
        builder: Callable[[EmbeddingConfig], BaseEmbeddingModel],
    ) -> None:
        """
        Register a provider builder.
        """
        self._builders[provider] = builder

    def create(
        self,
        config: EmbeddingConfig,
    ) -> BaseEmbeddingModel:
        """
        Create an embedding model.
        """
        if config.provider not in self._builders:
            available = ", ".join(sorted(self._builders)) or "none"
            raise ValueError(
                f"Unknown embedding provider '{config.provider}'. "
                f"Available providers: {available}"
            )

        return self._builders[config.provider](config)

    @property
    def providers(self) -> list[str]:
        """
        Registered provider names.
        """
        return sorted(self._builders.keys())