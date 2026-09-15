"""
app/llm/config.py

Centralized LLM configuration.

This module contains configuration only.

Provider-specific execution belongs in:
    app/llm/providers/

Routing belongs in:
    app/llm/routing/

Application-facing execution belongs in:
    app/llm/manager.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .constants import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_RETRIES,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    DEFAULT_PROVIDER,
    DEFAULT_MODELS,
)


load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    """
    Immutable configuration shared by the LLM infrastructure.

    Provider-specific implementations may consume only the
    configuration values relevant to them.
    """

    api_key: str
    base_url: str
    default_model: str

    provider: str = DEFAULT_PROVIDER

    timeout: int = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_RETRIES
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS


def _get_int_env(
    name: str,
    default: int,
) -> int:
    """
    Read an integer environment variable safely.
    """

    raw = os.getenv(name)

    if raw is None:
        return default

    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"{name} must be an integer."
        ) from exc

    return value


def _get_float_env(
    name: str,
    default: float,
) -> float:
    """
    Read a float environment variable safely.
    """

    raw = os.getenv(name)

    if raw is None:
        return default

    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(
            f"{name} must be a number."
        ) from exc

    return value


def _get_default_model() -> str:
    """
    Resolve the canonical default model.

    DEFAULT_MODEL may override the first model in DEFAULT_MODELS,
    but the constants module remains the source of truth for
    fallback models.
    """

    configured = os.getenv("DEFAULT_MODEL")

    if configured and configured.strip():
        return configured.strip()

    return DEFAULT_MODELS[0]


config = LLMConfig(
    api_key=os.getenv(
        "OPENROUTER_API_KEY",
        "",
    ).strip(),

    base_url=os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    ).strip(),

    default_model=_get_default_model(),

    provider=os.getenv(
        "LLM_PROVIDER",
        DEFAULT_PROVIDER,
    ).strip().lower(),

    timeout=_get_int_env(
        "LLM_TIMEOUT",
        DEFAULT_TIMEOUT,
    ),

    max_retries=_get_int_env(
        "LLM_MAX_RETRIES",
        DEFAULT_RETRIES,
    ),

    temperature=_get_float_env(
        "LLM_TEMPERATURE",
        DEFAULT_TEMPERATURE,
    ),

    max_tokens=_get_int_env(
        "LLM_MAX_TOKENS",
        DEFAULT_MAX_TOKENS,
    ),
)


def validate_config() -> None:
    """
    Validate LLM configuration.

    This should be called during application startup.

    Keeping validation explicit avoids surprising import-time
    failures when modules are imported for testing.
    """

    if not config.api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set."
        )

    if not config.base_url:
        raise ValueError(
            "OPENROUTER_BASE_URL cannot be empty."
        )

    if not config.default_model:
        raise ValueError(
            "DEFAULT_MODEL cannot be empty."
        )

    if not config.provider:
        raise ValueError(
            "LLM_PROVIDER cannot be empty."
        )

    if config.timeout <= 0:
        raise ValueError(
            "LLM_TIMEOUT must be greater than zero."
        )

    if config.max_retries < 0:
        raise ValueError(
            "LLM_MAX_RETRIES cannot be negative."
        )

    if config.temperature < 0:
        raise ValueError(
            "LLM_TEMPERATURE cannot be negative."
        )

    if config.max_tokens <= 0:
        raise ValueError(
            "LLM_MAX_TOKENS must be greater than zero."
        )