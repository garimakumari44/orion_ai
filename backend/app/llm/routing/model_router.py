"""
app/llm/routing/model_router.py

Canonical LLM Model Router
==========================

Responsible for selecting:

    provider + model

This module NEVER:

    - invokes an LLM API
    - performs retries
    - executes fallback
    - creates providers
    - truncates context

Routing modes
-------------

    free
        Prefer OpenRouter's canonical free router:

            openrouter/free

        Local providers are used only when OpenRouter is unavailable.

    paid
        Normal configured provider/model routing.

    auto
        Normal routing policy with runtime fallback handled elsewhere.

Architecture

    Agent / Planner / Service
              |
              v
         LLMManager
              |
              v
         ModelRouter
              |
              v
       RouteDecision
              |
              v
      ProviderRouter
              |
              v
       BaseLLMProvider
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional

from app.llm.constants import (
    DEFAULT_PROVIDER,
    DEFAULT_TASK,
    OPENROUTER,
    TASK_ALIASES,
    TASK_MODELS,
    TASK_FALLBACK_MODELS,
)

from app.llm.providers.base import BaseLLMProvider


# ============================================================================
# CONSTANTS
# ============================================================================

FREE_ROUTER_MODEL = "openrouter/free"

LLM_MODE_FREE = "free"
LLM_MODE_PAID = "paid"
LLM_MODE_AUTO = "auto"

VALID_LLM_MODES = frozenset(
    {
        LLM_MODE_FREE,
        LLM_MODE_PAID,
        LLM_MODE_AUTO,
    }
)

LOCAL_FREE_PROVIDERS = (
    "ollama",
    "lmstudio",
    "local",
)


# ============================================================================
# ROUTE DECISION
# ============================================================================


@dataclass(
    slots=True,
    frozen=True,
)
class RouteDecision:
    """
    Immutable provider/model routing decision.
    """

    provider: str
    model: str
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.provider, str):
            raise TypeError(
                "RouteDecision.provider must be a string."
            )

        if not isinstance(self.model, str):
            raise TypeError(
                "RouteDecision.model must be a string."
            )

        if not isinstance(self.reason, str):
            raise TypeError(
                "RouteDecision.reason must be a string."
            )

        provider = self.provider.strip().lower()
        model = self.model.strip()
        reason = self.reason.strip()

        if not provider:
            raise ValueError(
                "RouteDecision.provider cannot be empty."
            )

        if not model:
            raise ValueError(
                "RouteDecision.model cannot be empty."
            )

        if not reason:
            raise ValueError(
                "RouteDecision.reason cannot be empty."
            )

        object.__setattr__(
            self,
            "provider",
            provider,
        )

        object.__setattr__(
            self,
            "model",
            model,
        )

        object.__setattr__(
            self,
            "reason",
            reason,
        )


# ============================================================================
# MODEL ROUTER
# ============================================================================


class ModelRouter:
    """
    Canonical provider/model selection layer.

    The router decides WHERE and WHAT model should be used.

    It does not execute the selected model.

    Responsibilities
    ----------------
    - task normalization
    - provider selection
    - model selection
    - free/paid/auto policy
    - explicit provider/model handling
    - deterministic route decisions

    It does NOT:
    - call APIs
    - retry
    - execute fallback
    - create providers
    - truncate context
    """

    def __init__(
        self,
        providers: Dict[
            str,
            BaseLLMProvider,
        ],
        *,
        mode: Optional[str] = None,
    ) -> None:

        if not isinstance(
            providers,
            dict,
        ):
            raise TypeError(
                "providers must be a dictionary."
            )

        self._providers: Dict[
            str,
            BaseLLMProvider,
        ] = {}

        configured_mode = (
            mode
            if mode is not None
            else os.getenv(
                "ORION_LLM_MODE",
                LLM_MODE_FREE,
            )
        )

        self._mode = self._normalize_mode(
            configured_mode
        )

        for name, provider in providers.items():
            self.register_provider(
                name,
                provider,
            )

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def free_only(self) -> bool:
        return self._mode == LLM_MODE_FREE

    @property
    def paid_only(self) -> bool:
        return self._mode == LLM_MODE_PAID

    @property
    def auto_mode(self) -> bool:
        return self._mode == LLM_MODE_AUTO

    # ========================================================================
    # ROUTE
    # ========================================================================

    def route(
        self,
        *,
        task: str = DEFAULT_TASK,
        prompt: str = "",
        max_tokens: int = 512,
        prefer_provider: Optional[str] = None,
        prefer_model: Optional[str] = None,
    ) -> RouteDecision:
        """
        Resolve a canonical provider/model pair.
        """

        if not isinstance(
            task,
            str,
        ):
            raise TypeError(
                "task must be a string."
            )

        if not isinstance(
            prompt,
            str,
        ):
            raise TypeError(
                "prompt must be a string."
            )

        if (
            isinstance(
                max_tokens,
                bool,
            )
            or not isinstance(
                max_tokens,
                int,
            )
        ):
            raise TypeError(
                "max_tokens must be an integer."
            )

        if max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than zero."
            )

        normalized_task = self.normalize_task(
            task
        )

        explicit_provider = (
            self._normalize_optional(
                prefer_provider
            )
        )

        explicit_model = (
            self._normalize_optional_model(
                prefer_model
            )
        )

        # ====================================================================
        # FREE MODE
        # ====================================================================

        if self.free_only:
            return self._route_free(
                task=normalized_task,
                explicit_provider=explicit_provider,
                explicit_model=explicit_model,
            )

        # ====================================================================
        # EXPLICIT PROVIDER + MODEL
        # ====================================================================

        if (
            explicit_provider
            and explicit_model
        ):
            return self._route_explicit_provider_model(
                provider_name=explicit_provider,
                model=explicit_model,
            )

        # ====================================================================
        # EXPLICIT PROVIDER
        # ====================================================================

        if explicit_provider:
            return self._route_explicit_provider(
                provider_name=explicit_provider,
                task=normalized_task,
            )

        # ====================================================================
        # EXPLICIT MODEL
        # ====================================================================

        if explicit_model:
            return self._route_explicit_model(
                model=explicit_model
            )

        # ====================================================================
        # TASK ROUTING
        # ====================================================================

        for (
            provider_name,
            reason,
        ) in self._task_candidates(
            task=normalized_task,
            prompt=prompt,
        ):
            provider = self._providers.get(
                provider_name
            )

            if provider is None:
                continue

            if not self._provider_available(
                provider
            ):
                continue

            try:
                model = self._model_for_task(
                    provider=provider,
                    task=normalized_task,
                )
            except (
                RuntimeError,
                ValueError,
            ):
                continue

            return RouteDecision(
                provider=provider_name,
                model=model,
                reason=reason,
            )

        # ====================================================================
        # DEFAULT PROVIDER
        # ====================================================================

        default_provider = default_provider_name()

        provider = self._providers.get(
            default_provider
        )

        if (
            provider is not None
            and self._provider_available(provider)
        ):
            try:
                model = self._model_for_task(
                    provider=provider,
                    task=normalized_task,
                )
            except (
                RuntimeError,
                ValueError,
            ):
                model = None

            if model:
                return RouteDecision(
                    provider=default_provider,
                    model=model,
                    reason="Default provider",
                )

        # ====================================================================
        # SAFE REGISTERED PROVIDER FALLBACK
        # ====================================================================

        for (
            provider_name,
            provider,
        ) in self._providers.items():

            if not self._provider_available(
                provider
            ):
                continue

            try:
                model = provider.default_model()
            except Exception:
                continue

            model = self._normalize_model(
                model
            )

            if not model:
                continue

            if not self._provider_supports_model(
                provider,
                model,
            ):
                continue

            return RouteDecision(
                provider=provider_name,
                model=model,
                reason=(
                    f"Fallback provider "
                    f"'{provider_name}'"
                ),
            )

        raise RuntimeError(
            "No LLM providers are currently available."
        )

    # ========================================================================
    # FREE ROUTING
    # ========================================================================

    def _route_free(
        self,
        *,
        task: str,
        explicit_provider: Optional[str],
        explicit_model: Optional[str],
    ) -> RouteDecision:
        """
        Route exclusively toward free inference.

        Priority:

            1. Explicit local/free provider
            2. Explicit OpenRouter free model
            3. OpenRouter dynamic free router
            4. Local provider fallback
        """

        # --------------------------------------------------------------------
        # Explicit provider
        # --------------------------------------------------------------------

        if explicit_provider:

            # OpenRouter is handled separately because free routing has
            # a canonical dynamic endpoint.
            if explicit_provider == OPENROUTER:
                if explicit_model:
                    return self._route_openrouter_free_model(
                        explicit_model
                    )

                provider = self._require_provider(
                    OPENROUTER
                )

                self._require_available(
                    OPENROUTER,
                    provider,
                )

                return RouteDecision(
                    provider=OPENROUTER,
                    model=FREE_ROUTER_MODEL,
                    reason=(
                        "Free mode: OpenRouter dynamic "
                        "free-model router"
                    ),
                )

            # Local/free provider.
            if explicit_provider not in LOCAL_FREE_PROVIDERS:
                raise ValueError(
                    "Free LLM mode cannot use non-free "
                    f"provider '{explicit_provider}'."
                )

            provider = self._require_provider(
                explicit_provider
            )

            self._require_available(
                explicit_provider,
                provider,
            )

            model = (
                explicit_model
                or self._model_for_task(
                    provider=provider,
                    task=task,
                )
            )

            if not self._provider_supports_model(
                provider,
                model,
            ):
                raise ValueError(
                    f"Model '{model}' is not supported by "
                    f"provider '{explicit_provider}'."
                )

            return RouteDecision(
                provider=explicit_provider,
                model=model,
                reason=(
                    "Explicit local/free provider "
                    "selection"
                ),
            )

        # --------------------------------------------------------------------
        # Explicit model without provider
        # --------------------------------------------------------------------

        if explicit_model:

            if self._is_free_model(
                explicit_model
            ):
                return self._route_openrouter_free_model(
                    explicit_model
                )

            raise ValueError(
                "Free LLM mode cannot use paid model "
                f"'{explicit_model}'."
            )

        # --------------------------------------------------------------------
        # Canonical OpenRouter free router
        # --------------------------------------------------------------------

        provider = self._providers.get(
            OPENROUTER
        )

        if (
            provider is not None
            and self._provider_available(provider)
        ):
            return RouteDecision(
                provider=OPENROUTER,
                model=FREE_ROUTER_MODEL,
                reason=(
                    "Free mode: OpenRouter dynamic "
                    "free-model router"
                ),
            )

        # --------------------------------------------------------------------
        # Local fallback
        # --------------------------------------------------------------------

        for provider_name in LOCAL_FREE_PROVIDERS:

            provider = self._providers.get(
                provider_name
            )

            if provider is None:
                continue

            if not self._provider_available(
                provider
            ):
                continue

            try:
                model = self._model_for_task(
                    provider=provider,
                    task=task,
                )
            except (
                RuntimeError,
                ValueError,
            ):
                try:
                    model = provider.default_model()
                except Exception:
                    continue

            model = self._normalize_model(
                model
            )

            if not model:
                continue

            if not self._provider_supports_model(
                provider,
                model,
            ):
                continue

            return RouteDecision(
                provider=provider_name,
                model=model,
                reason=(
                    "Free mode: local provider fallback"
                ),
            )

        raise RuntimeError(
            "Free LLM mode is enabled, but no free "
            "OpenRouter or local provider is available."
        )

    # ========================================================================
    # EXPLICIT ROUTING
    # ========================================================================

    def _route_explicit_provider_model(
        self,
        *,
        provider_name: str,
        model: str,
    ) -> RouteDecision:

        provider = self._require_provider(
            provider_name
        )

        self._require_available(
            provider_name,
            provider,
        )

        if not self._provider_supports_model(
            provider,
            model,
        ):
            raise ValueError(
                f"Model '{model}' is not supported by "
                f"provider '{provider_name}'."
            )

        return RouteDecision(
            provider=provider_name,
            model=model,
            reason=(
                "Explicit provider and model selection"
            ),
        )

    def _route_explicit_provider(
        self,
        *,
        provider_name: str,
        task: str,
    ) -> RouteDecision:

        provider = self._require_provider(
            provider_name
        )

        self._require_available(
            provider_name,
            provider,
        )

        model = self._model_for_task(
            provider=provider,
            task=task,
        )

        return RouteDecision(
            provider=provider_name,
            model=model,
            reason="Explicit provider selection",
        )

    def _route_explicit_model(
        self,
        *,
        model: str,
    ) -> RouteDecision:

        for (
            provider_name,
            provider,
        ) in self._providers.items():

            if not self._provider_available(
                provider
            ):
                continue

            if not self._provider_supports_model(
                provider,
                model,
            ):
                continue

            return RouteDecision(
                provider=provider_name,
                model=model,
                reason="Explicit model selection",
            )

        raise ValueError(
            f"Model '{model}' is not available from any "
            "registered provider."
        )

    # ========================================================================
    # OPENROUTER FREE MODEL
    # ========================================================================

    def _route_openrouter_free_model(
        self,
        model: str,
    ) -> RouteDecision:

        if not self._is_free_model(model):
            raise ValueError(
                "Free LLM mode cannot use paid OpenRouter "
                f"model '{model}'."
            )

        provider = self._require_provider(
            OPENROUTER
        )

        self._require_available(
            OPENROUTER,
            provider,
        )

        # The dynamic free router is a valid OpenRouter target even if the
        # provider's configured model list does not explicitly enumerate it.
        if model == FREE_ROUTER_MODEL:
            return RouteDecision(
                provider=OPENROUTER,
                model=model,
                reason=(
                    "Explicit OpenRouter free router selection"
                ),
            )

        # Individual :free models must be accepted by the provider.
        if not self._provider_supports_model(
            provider,
            model,
        ):
            raise ValueError(
                f"Free model '{model}' is not supported by "
                "the OpenRouter provider."
            )

        return RouteDecision(
            provider=OPENROUTER,
            model=model,
            reason=(
                "Explicit free OpenRouter model"
            ),
        )

    # ========================================================================
    # TASK POLICY
    # ========================================================================

    def _task_candidates(
        self,
        *,
        task: str,
        prompt: str,
    ) -> list[
        tuple[str, str]
    ]:
        """
        Return ordered provider candidates.

        Provider ordering is intentionally conservative.

        OpenRouter remains the canonical provider today while additional
        providers can be registered later.
        """

        del prompt

        if task == "code":
            return [
                (
                    OPENROUTER,
                    "Coding workload",
                ),
                (
                    "openai",
                    "Coding workload fallback",
                ),
                (
                    "anthropic",
                    "Coding workload fallback",
                ),
            ]

        if task == "reasoning":
            return [
                (
                    OPENROUTER,
                    "Complex reasoning",
                ),
                (
                    "anthropic",
                    "Reasoning provider fallback",
                ),
                (
                    "openai",
                    "Reasoning provider fallback",
                ),
            ]

        if task == "fast":
            return [
                (
                    OPENROUTER,
                    "Low-latency workload",
                ),
                (
                    "gemini",
                    "Low-latency provider fallback",
                ),
                (
                    "ollama",
                    "Local low-latency fallback",
                ),
            ]

        if task == "vision":
            return [
                (
                    OPENROUTER,
                    "Vision workload",
                ),
                (
                    "openai",
                    "Vision provider fallback",
                ),
                (
                    "gemini",
                    "Vision provider fallback",
                ),
            ]

        if task == "cheap":
            return [
                (
                    "ollama",
                    "Cost-optimised local execution",
                ),
                (
                    OPENROUTER,
                    "Cost-optimised execution",
                ),
                (
                    "gemini",
                    "Cost-optimised fallback",
                ),
            ]

        return [
            (
                default_provider_name(),
                "Default routing",
            )
        ]

    # ========================================================================
    # MODEL RESOLUTION
    # ========================================================================

    @staticmethod
    def _model_for_task(
        *,
        provider: BaseLLMProvider,
        task: str,
    ) -> str:
        """
        Resolve the configured model for a task.

        Provider-specific configuration has priority.

        Global TASK_MODELS is used as policy information, but only when
        the provider actually supports that model.

        Otherwise the provider's own default model is used.
        """

        configured_models = (
            provider.configured_models()
        )

        if not isinstance(
            configured_models,
            dict,
        ):
            configured_models = {}

        task_model = configured_models.get(
            task
        )

        if task_model:
            task_model = ModelRouter._normalize_model(
                task_model
            )

            if task_model and ModelRouter._provider_supports_model(
                provider,
                task_model,
            ):
                return task_model

        # If this provider has no explicit task model, consult canonical
        # application policy.
        policy_model = TASK_MODELS.get(
            task
        )

        if policy_model:
            policy_model = ModelRouter._normalize_model(
                policy_model
            )

            if (
                policy_model
                and ModelRouter._provider_supports_model(
                    provider,
                    policy_model,
                )
            ):
                return policy_model

        # Provider default is the final provider-local choice.
        try:
            default_model = provider.default_model()
        except Exception as exc:
            raise RuntimeError(
                "Provider failed to return its default model."
            ) from exc

        default_model = ModelRouter._normalize_model(
            default_model
        )

        if not default_model:
            raise RuntimeError(
                "Provider returned an invalid default model."
            )

        if not ModelRouter._provider_supports_model(
            provider,
            default_model,
        ):
            raise RuntimeError(
                f"Provider '{provider.provider_name}' "
                f"does not support its default model "
                f"'{default_model}'."
            )

        return default_model

    # ========================================================================
    # PROVIDER ACCESS
    # ========================================================================

    def get_provider(
        self,
        decision: RouteDecision,
    ) -> BaseLLMProvider:

        if not isinstance(
            decision,
            RouteDecision,
        ):
            raise TypeError(
                "decision must be a RouteDecision."
            )

        provider = self._providers.get(
            decision.provider.strip().lower()
        )

        if provider is None:
            raise ValueError(
                f"Provider '{decision.provider}' "
                "is not registered."
            )

        return provider

    # ========================================================================
    # REGISTRATION
    # ========================================================================

    def register_provider(
        self,
        name: str,
        provider: BaseLLMProvider,
    ) -> None:

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Provider name must be a string."
            )

        if not isinstance(
            provider,
            BaseLLMProvider,
        ):
            raise TypeError(
                "provider must be a BaseLLMProvider."
            )

        normalized_name = (
            name.strip().lower()
        )

        if not normalized_name:
            raise ValueError(
                "Provider name cannot be empty."
            )

        self._providers[
            normalized_name
        ] = provider

    def unregister_provider(
        self,
        name: str,
    ) -> None:

        if not isinstance(
            name,
            str,
        ):
            return

        self._providers.pop(
            name.strip().lower(),
            None,
        )

    # ========================================================================
    # PROVIDER INFORMATION
    # ========================================================================

    def available_providers(
        self,
    ) -> list[str]:

        result: list[str] = []

        for (
            name,
            provider,
        ) in self._providers.items():

            if self._provider_available(
                provider
            ):
                result.append(name)

        return result

    def registered_providers(
        self,
    ) -> list[str]:

        return list(
            self._providers.keys()
        )

    # ========================================================================
    # TASK NORMALIZATION
    # ========================================================================

    @staticmethod
    def normalize_task(
        task: str,
    ) -> str:
        """
        Normalize arbitrary application task terminology into a canonical
        task identifier.

        Unknown tasks are preserved as normalized strings so future task
        policies remain extensible.
        """

        if not isinstance(
            task,
            str,
        ):
            raise TypeError(
                "task must be a string."
            )

        value = task.strip().lower()

        if not value:
            raise ValueError(
                "task cannot be empty."
            )

        return TASK_ALIASES.get(
            value,
            value,
        )

    # ========================================================================
    # MODE NORMALIZATION
    # ========================================================================

    @staticmethod
    def _normalize_mode(
        value: Optional[str],
    ) -> str:

        if not isinstance(
            value,
            str,
        ):
            return LLM_MODE_FREE

        value = value.strip().lower()

        if value not in VALID_LLM_MODES:
            raise ValueError(
                "Invalid ORION_LLM_MODE. "
                f"Expected one of: "
                f"{sorted(VALID_LLM_MODES)}; "
                f"received '{value}'."
            )

        return value

    # ========================================================================
    # PROVIDER HELPERS
    # ========================================================================

    def _require_provider(
        self,
        provider_name: str,
    ) -> BaseLLMProvider:

        provider = self._providers.get(
            provider_name
        )

        if provider is None:
            raise ValueError(
                f"Provider '{provider_name}' "
                "is not registered."
            )

        return provider

    @staticmethod
    def _require_available(
        provider_name: str,
        provider: BaseLLMProvider,
    ) -> None:

        if not ModelRouter._provider_available(
            provider
        ):
            raise RuntimeError(
                f"Provider '{provider_name}' "
                "is currently unavailable."
            )

    @staticmethod
    def _provider_available(
        provider: BaseLLMProvider,
    ) -> bool:

        try:
            return bool(
                provider.is_available()
            )
        except Exception:
            return False

    @staticmethod
    def _provider_supports_model(
        provider: BaseLLMProvider,
        model: str,
    ) -> bool:

        try:
            return bool(
                provider.supports_model(
                    model
                )
            )
        except Exception:
            return False

    # ========================================================================
    # MODEL HELPERS
    # ========================================================================

    @staticmethod
    def _normalize_model(
        value: object,
    ) -> Optional[str]:

        if not isinstance(
            value,
            str,
        ):
            return None

        value = value.strip()

        return value or None

    @staticmethod
    def _is_free_model(
        model: str,
    ) -> bool:

        normalized = model.strip().lower()

        return (
            normalized == FREE_ROUTER_MODEL
            or normalized.endswith(":free")
        )

    # ========================================================================
    # NORMALIZATION
    # ========================================================================

    @staticmethod
    def _normalize_optional(
        value: Optional[str],
    ) -> Optional[str]:

        if not isinstance(
            value,
            str,
        ):
            return None

        value = value.strip().lower()

        return value or None

    @staticmethod
    def _normalize_optional_model(
        value: Optional[str],
    ) -> Optional[str]:

        if not isinstance(
            value,
            str,
        ):
            return None

        value = value.strip()

        return value or None


# ============================================================================
# DEFAULT PROVIDER
# ============================================================================


def default_provider_name() -> str:
    """
    Return the canonical configured default provider.
    """

    if isinstance(
        DEFAULT_PROVIDER,
        str,
    ):
        value = (
            DEFAULT_PROVIDER
            .strip()
            .lower()
        )

        if value:
            return value

    return OPENROUTER