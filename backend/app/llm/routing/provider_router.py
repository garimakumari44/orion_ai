"""
app/llm/routing/provider_router.py

Provider Registry / Resolver
============================

ProviderRouter does NOT select models.

ModelRouter decides:

    provider + model

ProviderRouter resolves:

    provider name -> provider instance
"""

from __future__ import annotations

from typing import Dict, Iterable

from app.llm.providers.base import BaseLLMProvider


class ProviderRouter:
    """
    Registry and resolver for LLM providers.

    This class deliberately contains no model-selection logic.
    """

    def __init__(
        self,
        providers: Dict[str, BaseLLMProvider] | None = None,
    ) -> None:

        self._providers: Dict[
            str,
            BaseLLMProvider,
        ] = {}

        if providers:
            for name, provider in providers.items():
                self.register(
                    name,
                    provider,
                )

    # ==================================================================
    # REGISTRATION
    # ==================================================================

    def register(
        self,
        name: str,
        provider: BaseLLMProvider,
    ) -> None:
        """
        Register a provider.
        """

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Provider name must be a string."
            )

        provider_name = name.strip().lower()

        if not provider_name:
            raise ValueError(
                "Provider name cannot be empty."
            )

        if not isinstance(
            provider,
            BaseLLMProvider,
        ):
            raise TypeError(
                "provider must be an instance of "
                "BaseLLMProvider."
            )

        self._providers[
            provider_name
        ] = provider

    # ==================================================================
    # UNREGISTER
    # ==================================================================

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.

        Missing providers are ignored.
        """

        if not isinstance(
            name,
            str,
        ):
            return

        self._providers.pop(
            name.strip().lower(),
            None,
        )

    # ==================================================================
    # RESOLVE
    # ==================================================================

    def resolve(
        self,
        provider: str,
    ) -> BaseLLMProvider:
        """
        Resolve a registered provider.
        """

        if not isinstance(
            provider,
            str,
        ):
            raise TypeError(
                "provider must be a string."
            )

        provider_name = provider.strip().lower()

        if not provider_name:
            raise ValueError(
                "provider cannot be empty."
            )

        instance = self._providers.get(
            provider_name
        )

        if instance is None:
            raise ValueError(
                f"Provider '{provider_name}' "
                "is not registered."
            )

        return instance

    # ==================================================================
    # MANAGER COMPATIBILITY
    # ==================================================================

    def get_client(
        self,
        *,
        provider: str,
        model: str | None = None,
    ) -> BaseLLMProvider:
        """
        Resolve the provider selected by ModelRouter.

        The model is intentionally ignored here.

        ModelRouter has already decided:

            provider + model

        LLMManager passes the selected model to the provider's
        execution method.
        """

        del model

        return self.resolve(
            provider
        )

    # ==================================================================
    # AVAILABILITY
    # ==================================================================

    def is_available(
        self,
        provider: str,
    ) -> bool:
        """
        Return True if the provider is healthy.
        """

        try:
            instance = self.resolve(
                provider
            )

        except (
            TypeError,
            ValueError,
        ):
            return False

        try:
            return bool(
                instance.is_available()
            )

        except Exception:
            return False

    # ==================================================================
    # REGISTERED PROVIDERS
    # ==================================================================

    def registered_providers(self) -> list[str]:
        """
        Return all registered provider names.
        """

        return list(
            self._providers.keys()
        )

    # ==================================================================
    # AVAILABLE PROVIDERS
    # ==================================================================

    def available_providers(self) -> list[str]:
        """
        Return currently healthy providers.
        """

        available: list[str] = []

        for (
            name,
            provider,
        ) in self._providers.items():

            try:

                if provider.is_available():
                    available.append(name)

            except Exception:
                continue

        return available

    # ==================================================================
    # ITERATION
    # ==================================================================

    def providers(
        self,
    ) -> Iterable[
        tuple[str, BaseLLMProvider]
    ]:
        """
        Iterate over registered providers.
        """

        return self._providers.items()

    # ==================================================================
    # CONTAINMENT
    # ==================================================================

    def has(
        self,
        provider: str,
    ) -> bool:
        """
        Return True if provider is registered.
        """

        if not isinstance(
            provider,
            str,
        ):
            return False

        return (
            provider.strip().lower()
            in self._providers
        )

    # ==================================================================
    # LENGTH
    # ==================================================================

    def __len__(self) -> int:
        """
        Return number of registered providers.
        """

        return len(
            self._providers
        )

    # ==================================================================
    # REPRESENTATION
    # ==================================================================

    def __repr__(self) -> str:
        """
        Safe developer representation.
        """

        providers = ", ".join(
            self._providers.keys()
        )

        return (
            "ProviderRouter("
            f"providers=[{providers}]"
            ")"
        )