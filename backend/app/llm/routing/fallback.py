"""
app/llm/routing/fallback.py

Canonical LLM fallback strategy.

Responsibilities
----------------
- Build fallback provider/model candidates.
- Track attempted targets.
- Prevent duplicate attempts.
- Respect registered providers.
- Respect provider availability.
- Respect provider model support.
- Never execute API calls.
- Keep fallback policy centralized.

Architecture

    LLMManager
         |
         v
    FallbackStrategy
         |
         v
    FallbackTarget
         |
         v
    ProviderRouter
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from app.llm.constants import (
    DEFAULT_MODELS,
    MAX_FALLBACK_ATTEMPTS,
    OPENROUTER,
    TASK_FALLBACK_MODELS,
)

from app.llm.providers.base import (
    BaseLLMProvider,
)


# ============================================================================
# FALLBACK TARGET
# ============================================================================


@dataclass(
    slots=True,
    frozen=True,
)
class FallbackTarget:
    """
    Immutable provider/model fallback target.
    """

    provider: str
    model: str

    def __post_init__(self) -> None:

        if not isinstance(
            self.provider,
            str,
        ):
            raise TypeError(
                "FallbackTarget.provider must be a string."
            )

        if not isinstance(
            self.model,
            str,
        ):
            raise TypeError(
                "FallbackTarget.model must be a string."
            )

        provider = self.provider.strip().lower()
        model = self.model.strip()

        if not provider:
            raise ValueError(
                "FallbackTarget.provider cannot be empty."
            )

        if not model:
            raise ValueError(
                "FallbackTarget.model cannot be empty."
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


# ============================================================================
# FALLBACK STATE
# ============================================================================


@dataclass(slots=True)
class FallbackState:
    """
    State for one LLM execution attempt chain.

    A fresh state must be created for every request.
    """

    attempted: list[FallbackTarget] = field(
        default_factory=list
    )

    failures: list[str] = field(
        default_factory=list
    )

    def add_attempt(
        self,
        target: FallbackTarget,
        reason: str,
    ) -> None:

        if not isinstance(
            target,
            FallbackTarget,
        ):
            raise TypeError(
                "target must be a FallbackTarget."
            )

        if self.has_attempted(target):
            return

        self.attempted.append(target)

        self.failures.append(
            str(reason)
        )

    def has_attempted(
        self,
        target: FallbackTarget,
    ) -> bool:

        if not isinstance(
            target,
            FallbackTarget,
        ):
            raise TypeError(
                "target must be a FallbackTarget."
            )

        return (
            target.provider,
            target.model,
        ) in {
            (
                item.provider,
                item.model,
            )
            for item in self.attempted
        }


# ============================================================================
# FALLBACK STRATEGY
# ============================================================================


class FallbackStrategy:
    """
    Determines the next provider/model after an execution failure.

    This class NEVER:

        - executes LLM requests
        - performs HTTP retries
        - calls provider APIs
        - creates providers

    It only selects the next candidate.
    """

    # Infrastructure fallbacks are only used if those providers are actually
    # registered by the application factory.
    PROVIDER_FALLBACK_CHAIN: tuple[
        FallbackTarget,
        ...
    ] = (
        FallbackTarget(
            provider="openai",
            model="gpt-5",
        ),
        FallbackTarget(
            provider="anthropic",
            model="claude-3.7-sonnet",
        ),
        FallbackTarget(
            provider="gemini",
            model="gemini-2.5-pro",
        ),
        FallbackTarget(
            provider="ollama",
            model="llama3.2",
        ),
    )

    def __init__(
        self,
        chain: Optional[
            Iterable[FallbackTarget]
        ] = None,
        max_attempts: int = MAX_FALLBACK_ATTEMPTS,
    ) -> None:

        if (
            isinstance(
                max_attempts,
                bool,
            )
            or not isinstance(
                max_attempts,
                int,
            )
        ):
            raise TypeError(
                "max_attempts must be an integer."
            )

        if max_attempts <= 0:
            raise ValueError(
                "max_attempts must be greater than zero."
            )

        if chain is None:
            resolved_chain = (
                self._build_default_chain()
            )
        else:
            resolved_chain = list(chain)

        for target in resolved_chain:

            if not isinstance(
                target,
                FallbackTarget,
            ):
                raise TypeError(
                    "Fallback chain must contain "
                    "FallbackTarget instances."
                )

        self.chain = self._deduplicate(
            resolved_chain
        )

        self.max_attempts = max_attempts

    # ========================================================================
    # DEFAULT CHAIN
    # ========================================================================

    @staticmethod
    def _build_default_chain() -> list[FallbackTarget]:
        """
        Build the global canonical fallback chain.

        Order:

            1. task-specific OpenRouter models
            2. global OpenRouter models
            3. optional infrastructure providers
        """

        targets: list[FallbackTarget] = []

        # --------------------------------------------------------------------
        # Task-specific OpenRouter models
        # --------------------------------------------------------------------

        for models in TASK_FALLBACK_MODELS.values():

            if not isinstance(
                models,
                (list, tuple),
            ):
                continue

            for model in models:

                if not isinstance(
                    model,
                    str,
                ):
                    continue

                model = model.strip()

                if not model:
                    continue

                targets.append(
                    FallbackTarget(
                        provider=OPENROUTER,
                        model=model,
                    )
                )

        # --------------------------------------------------------------------
        # Global OpenRouter safety net
        # --------------------------------------------------------------------

        for model in DEFAULT_MODELS:

            if not isinstance(
                model,
                str,
            ):
                continue

            model = model.strip()

            if not model:
                continue

            targets.append(
                FallbackTarget(
                    provider=OPENROUTER,
                    model=model,
                )
            )

        # --------------------------------------------------------------------
        # Optional infrastructure fallbacks
        # --------------------------------------------------------------------

        targets.extend(
            FallbackStrategy.PROVIDER_FALLBACK_CHAIN
        )

        return FallbackStrategy._deduplicate(
            targets
        )

    # ========================================================================
    # DEDUPLICATION
    # ========================================================================

    @staticmethod
    def _deduplicate(
        targets: Iterable[FallbackTarget],
    ) -> list[FallbackTarget]:

        result: list[FallbackTarget] = []

        seen: set[
            tuple[str, str]
        ] = set()

        for target in targets:

            key = (
                target.provider,
                target.model,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(target)

        return result

    # ========================================================================
    # NEXT TARGET
    # ========================================================================

    def next_target(
        self,
        state: FallbackState,
        *,
        providers: Optional[
            dict[str, BaseLLMProvider]
        ] = None,
    ) -> Optional[FallbackTarget]:
        """
        Return the next valid unused target.

        If providers is supplied, the target must:

            - be registered
            - be available
            - support the model
        """

        if not isinstance(
            state,
            FallbackState,
        ):
            raise TypeError(
                "state must be a FallbackState."
            )

        if len(
            state.attempted
        ) >= self.max_attempts:
            return None

        attempted = {
            (
                target.provider,
                target.model,
            )
            for target in state.attempted
        }

        for target in self.chain:

            target_key = (
                target.provider,
                target.model,
            )

            if target_key in attempted:
                continue

            # ---------------------------------------------------------------
            # Registry filtering
            # ---------------------------------------------------------------

            if providers is not None:

                provider = providers.get(
                    target.provider
                )

                if provider is None:
                    continue

                # -----------------------------------------------------------
                # Availability
                # -----------------------------------------------------------

                try:
                    if not provider.is_available():
                        continue
                except Exception:
                    continue

                # -----------------------------------------------------------
                # Model support
                # -----------------------------------------------------------

                # openrouter/free is a canonical dynamic target and may not
                # appear in the provider's static configured model list.
                if (
                    target.provider == OPENROUTER
                    and target.model == "openrouter/free"
                ):
                    return target

                try:
                    if not provider.supports_model(
                        target.model
                    ):
                        continue
                except Exception:
                    continue

            return target

        return None

    # ========================================================================
    # EXHAUSTED
    # ========================================================================

    def exhausted(
        self,
        state: FallbackState,
        *,
        providers: Optional[
            dict[str, BaseLLMProvider]
        ] = None,
    ) -> bool:

        return (
            self.next_target(
                state,
                providers=providers,
            )
            is None
        )

    # ========================================================================
    # RESET
    # ========================================================================

    def reset(self) -> FallbackState:
        return FallbackState()

    # ========================================================================
    # CHAIN
    # ========================================================================

    def configured_chain(
        self,
    ) -> list[FallbackTarget]:

        return list(
            self.chain
        )

    # ========================================================================
    # REPRESENTATION
    # ========================================================================

    def __repr__(self) -> str:

        return (
            "FallbackStrategy("
            f"max_attempts={self.max_attempts}, "
            f"chain={self.chain!r}"
            ")"
        )