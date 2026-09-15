"""
app/llm/factory.py

Canonical LLM infrastructure factory.

Responsibilities
----------------
- Construct concrete providers.
- Build the shared provider registry.
- Construct ModelRouter.
- Construct ProviderRouter.
- Construct ContextBudget.
- Construct the canonical LLMManager.

This module creates infrastructure only.

It does NOT:

    - execute LLM requests
    - perform retries
    - perform fallback
    - select fallback targets
    - contain application-level LLM logic
"""

from __future__ import annotations

import os
from typing import Dict

from app.llm.constants import (
    DEFAULT_MODELS,
    DEFAULT_PROVIDER,
    DEFAULT_TIMEOUT,
    TASK_MODELS,
)

from app.llm.context import (
    ContextBudget,
    DEFAULT_CONTEXT_BUDGET,
)

from app.llm.manager import (
    LLMManager,
)

from app.llm.providers.base import (
    BaseLLMProvider,
)

from app.llm.providers.openrouter import (
    OpenRouterProvider,
)

from app.llm.routing.model_router import (
    ModelRouter,
)

from app.llm.routing.provider_router import (
    ProviderRouter,
)


# ============================================================================
# OPENROUTER PROVIDER
# ============================================================================


def _create_openrouter_provider() -> OpenRouterProvider:
    """
    Construct the canonical OpenRouter provider.
    """

    api_key = os.getenv(
        "OPENROUTER_API_KEY",
        "",
    ).strip()

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    # ------------------------------------------------------------------------
    # Default model
    # ------------------------------------------------------------------------

    if not DEFAULT_MODELS:
        raise RuntimeError(
            "DEFAULT_MODELS cannot be empty."
        )

    model = DEFAULT_MODELS[0]

    if not isinstance(
        model,
        str,
    ):
        raise RuntimeError(
            "Default OpenRouter model must be a string."
        )

    model = model.strip()

    if not model:
        raise RuntimeError(
            "No default OpenRouter model is configured."
        )

    # ------------------------------------------------------------------------
    # Base URL
    # ------------------------------------------------------------------------

    base_url = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    ).strip()

    if not base_url:
        base_url = (
            "https://openrouter.ai/api/v1"
        )

    # ------------------------------------------------------------------------
    # Application identification
    # ------------------------------------------------------------------------

    app_name = os.getenv(
        "OPENROUTER_APP_NAME",
        "Orion AI System",
    ).strip()

    app_url = os.getenv(
        "OPENROUTER_APP_URL",
        "",
    ).strip()

    # ------------------------------------------------------------------------
    # Timeout
    # ------------------------------------------------------------------------

    timeout_raw = os.getenv(
        "OPENROUTER_TIMEOUT",
        str(DEFAULT_TIMEOUT),
    ).strip()

    try:
        timeout = float(
            timeout_raw
        )
    except (
        TypeError,
        ValueError,
    ):
        timeout = float(
            DEFAULT_TIMEOUT
        )

    if timeout <= 0:
        timeout = float(
            DEFAULT_TIMEOUT
        )

    # ------------------------------------------------------------------------
    # Task models
    # ------------------------------------------------------------------------

    if not isinstance(
        TASK_MODELS,
        dict,
    ):
        raise RuntimeError(
            "TASK_MODELS must be a dictionary."
        )

    normalized_task_models: dict[
        str,
        str,
    ] = {}

    for (
        task_name,
        model_name,
    ) in TASK_MODELS.items():

        if not isinstance(
            task_name,
            str,
        ):
            continue

        if not isinstance(
            model_name,
            str,
        ):
            continue

        normalized_task = (
            task_name.strip().lower()
        )

        normalized_model = (
            model_name.strip()
        )

        if not normalized_task:
            continue

        if not normalized_model:
            continue

        normalized_task_models[
            normalized_task
        ] = normalized_model

    # ------------------------------------------------------------------------
    # Provider
    # ------------------------------------------------------------------------

    return OpenRouterProvider(
        api_key=api_key,
        model=model,
        base_url=base_url,
        app_name=(
            app_name
            or None
        ),
        app_url=(
            app_url
            or None
        ),
        timeout=timeout,
        task_models=normalized_task_models,
    )


# ============================================================================
# OPTIONAL PROVIDER CREATION
# ============================================================================


def _openrouter_is_configured() -> bool:
    """
    Return True when OpenRouter credentials exist.

    This check allows local-only deployments to start without an
    OpenRouter API key.
    """

    return bool(
        os.getenv(
            "OPENROUTER_API_KEY",
            "",
        ).strip()
    )


# ============================================================================
# PROVIDER REGISTRY
# ============================================================================


def _create_providers() -> Dict[
    str,
    BaseLLMProvider,
]:
    """
    Construct the canonical provider registry.

    OpenRouter is currently the only concrete remote provider.

    It is registered only when credentials are configured.

    This is important for:

        ORION_LLM_MODE=free

    because the router can then operate with a future local provider
    without factory startup failing solely because OpenRouter credentials
    are absent.
    """

    providers: Dict[
        str,
        BaseLLMProvider,
    ] = {}

    # ------------------------------------------------------------------------
    # OpenRouter
    # ------------------------------------------------------------------------

    if _openrouter_is_configured():
        providers[
            "openrouter"
        ] = _create_openrouter_provider()

    return providers


# ============================================================================
# LLM MANAGER
# ============================================================================


def create_llm_manager() -> LLMManager:
    """
    Construct the canonical application-wide LLMManager.
    """

    providers = _create_providers()

    if not providers:
        raise RuntimeError(
            "No LLM providers were registered. "
            "Configure OPENROUTER_API_KEY or register "
            "a local provider in the LLM factory."
        )

    # ------------------------------------------------------------------------
    # Default provider
    # ------------------------------------------------------------------------

    normalized_default_provider = (
        DEFAULT_PROVIDER.strip().lower()
        if isinstance(
            DEFAULT_PROVIDER,
            str,
        )
        else ""
    )

    if not normalized_default_provider:
        raise RuntimeError(
            "DEFAULT_PROVIDER cannot be empty."
        )

    # Do NOT require DEFAULT_PROVIDER to be registered when the application
    # is explicitly running in free mode with a local provider.
    #
    # ModelRouter is responsible for selecting an actually available
    # provider.

    llm_mode = os.getenv(
        "ORION_LLM_MODE",
        "free",
    ).strip().lower()

    if (
        normalized_default_provider not in providers
        and llm_mode in {
            "paid",
            "auto",
        }
    ):
        raise RuntimeError(
            "Configured DEFAULT_PROVIDER "
            f"'{normalized_default_provider}' "
            "is not registered."
        )

    # ------------------------------------------------------------------------
    # Model Router
    # ------------------------------------------------------------------------

    model_router = ModelRouter(
        providers=providers,
        mode=llm_mode,
    )

    # ------------------------------------------------------------------------
    # Provider Router
    # ------------------------------------------------------------------------

    provider_router = ProviderRouter(
        providers=providers,
    )

    # ------------------------------------------------------------------------
    # Context Budget
    # ------------------------------------------------------------------------

    context_budget = ContextBudget(
        max_context_tokens=DEFAULT_CONTEXT_BUDGET,
    )

    # ------------------------------------------------------------------------
    # Manager
    # ------------------------------------------------------------------------

    manager = LLMManager(
        model_router=model_router,
        provider_router=provider_router,
        context_budget=context_budget,
    )

    return manager