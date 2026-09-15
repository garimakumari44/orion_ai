"""
Embedding Manager.

Registers embedding providers and exposes
a single interface to the rest of the system.
"""

from __future__ import annotations

from typing import Dict

from .base import BaseEmbeddingModel


class EmbeddingManager:
    """
    Registry for embedding providers.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, BaseEmbeddingModel] = {}

    def register(
        self,
        provider: BaseEmbeddingModel,
    ) -> None:
        """
        Register an embedding provider.
        """
        self._providers[provider.provider] = provider

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.
        """
        self._providers.pop(name, None)

    def get(
        self,
        name: str,
    ) -> BaseEmbeddingModel:
        """
        Retrieve a provider by name.
        """
        if name not in self._providers:
            available = ", ".join(self._providers.keys()) or "none"
            raise ValueError(
                f"Unknown embedding provider '{name}'. "
                f"Available providers: {available}"
            )

        return self._providers[name]

    @property
    def providers(self) -> list[str]:
        """
        List registered providers.
        """
        return sorted(self._providers.keys())

    def clear(self) -> None:
        """
        Remove all providers.
        """
        self._providers.clear()