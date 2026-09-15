"""
app/llm/constants.py

Centralized LLM policy constants.

This module contains POLICY DATA ONLY.

It must NOT:

    - instantiate providers
    - perform HTTP requests
    - import provider implementations
    - execute routing
    - execute fallback
"""

from __future__ import annotations

from typing import Final


# ============================================================================
# PROVIDERS
# ============================================================================

OPENROUTER: Final[str] = "openrouter"

DEFAULT_PROVIDER: Final[str] = OPENROUTER


# ============================================================================
# SPECIAL ROUTING TARGETS
# ============================================================================

OPENROUTER_FREE_ROUTER: Final[str] = (
    "openrouter/free"
)


# ============================================================================
# MODEL IDENTIFIERS
# ============================================================================

LLAMA_3_70B: Final[str] = (
    "meta-llama/llama-3.3-70b-instruct"
)

GEMMA_4: Final[str] = (
    "google/gemma-4-26b-a4b-it:free"
)

MISTRAL_SMALL: Final[str] = (
    "mistralai/mistral-small-3.2-24b-instruct:free"
)

DEEPSEEK_CHAT: Final[str] = (
    "deepseek/deepseek-chat-v3-0324:free"
)

QWEN_32B: Final[str] = (
    "qwen/qwen3-32b:free"
)


# ============================================================================
# MODEL GROUPS
# ============================================================================

FREE_MODELS: Final[tuple[str, ...]] = (
    GEMMA_4,
    MISTRAL_SMALL,
    DEEPSEEK_CHAT,
    QWEN_32B,
)

GENERAL_TEXT_MODELS: Final[tuple[str, ...]] = (
    LLAMA_3_70B,
    GEMMA_4,
    MISTRAL_SMALL,
    DEEPSEEK_CHAT,
    QWEN_32B,
)


# ============================================================================
# DEFAULT MODEL
# ============================================================================

DEFAULT_MODEL: Final[str] = LLAMA_3_70B


DEFAULT_MODELS: Final[tuple[str, ...]] = (
    LLAMA_3_70B,
    GEMMA_4,
    MISTRAL_SMALL,
    DEEPSEEK_CHAT,
    QWEN_32B,
)


# ============================================================================
# TASK IDENTIFIERS
# ============================================================================

TASK_CHAT: Final[str] = "chat"

TASK_REASONING: Final[str] = "reasoning"

TASK_FAST: Final[str] = "fast"

TASK_CODE: Final[str] = "code"

TASK_VISION: Final[str] = "vision"

TASK_CHEAP: Final[str] = "cheap"


SUPPORTED_TASKS: Final[tuple[str, ...]] = (
    TASK_CHAT,
    TASK_REASONING,
    TASK_FAST,
    TASK_CODE,
    TASK_VISION,
    TASK_CHEAP,
)


# ============================================================================
# TASK ALIASES
# ============================================================================

TASK_ALIASES: Final[dict[str, str]] = {

    # General
    "chat": TASK_CHAT,
    "conversation": TASK_CHAT,
    "conversational": TASK_CHAT,
    "general": TASK_CHAT,
    "default": TASK_CHAT,

    # Reasoning
    "reasoning": TASK_REASONING,
    "analysis": TASK_REASONING,
    "analytical": TASK_REASONING,
    "research": TASK_REASONING,
    "research_analysis": TASK_REASONING,
    "financial_analysis": TASK_REASONING,
    "investment_analysis": TASK_REASONING,
    "planning": TASK_REASONING,
    "planner": TASK_REASONING,
    "complex": TASK_REASONING,

    # Fast
    "fast": TASK_FAST,
    "quick": TASK_FAST,
    "lightweight": TASK_FAST,
    "classification": TASK_FAST,
    "classify": TASK_FAST,
    "extraction": TASK_FAST,
    "extract": TASK_FAST,
    "routing": TASK_FAST,
    "router": TASK_FAST,
    "simple": TASK_FAST,

    # Code
    "code": TASK_CODE,
    "coding": TASK_CODE,
    "programming": TASK_CODE,
    "developer": TASK_CODE,
    "software": TASK_CODE,

    # Vision
    "vision": TASK_VISION,
    "image": TASK_VISION,
    "multimodal": TASK_VISION,

    # Cheap
    "cheap": TASK_CHEAP,
    "low_cost": TASK_CHEAP,
    "low-cost": TASK_CHEAP,
    "cost_optimized": TASK_CHEAP,
    "cost-optimized": TASK_CHEAP,
    "economical": TASK_CHEAP,
}


# ============================================================================
# PRIMARY TASK MODELS
# ============================================================================

MODEL_CHAT: Final[str] = LLAMA_3_70B

MODEL_REASONING: Final[str] = LLAMA_3_70B

MODEL_FAST: Final[str] = GEMMA_4

MODEL_CODE: Final[str] = QWEN_32B

MODEL_VISION: Final[str] = GEMMA_4

MODEL_CHEAP: Final[str] = MISTRAL_SMALL


TASK_MODELS: Final[dict[str, str]] = {
    TASK_CHAT: MODEL_CHAT,
    TASK_REASONING: MODEL_REASONING,
    TASK_FAST: MODEL_FAST,
    TASK_CODE: MODEL_CODE,
    TASK_VISION: MODEL_VISION,
    TASK_CHEAP: MODEL_CHEAP,
}


# ============================================================================
# TASK FALLBACK POLICY
# ============================================================================

TASK_FALLBACK_MODELS: Final[
    dict[str, list[str]]
] = {

    TASK_CHAT: [
        LLAMA_3_70B,
        GEMMA_4,
        MISTRAL_SMALL,
        DEEPSEEK_CHAT,
        QWEN_32B,
    ],

    TASK_REASONING: [
        LLAMA_3_70B,
        DEEPSEEK_CHAT,
        MISTRAL_SMALL,
        GEMMA_4,
    ],

    TASK_FAST: [
        GEMMA_4,
        MISTRAL_SMALL,
        DEEPSEEK_CHAT,
        LLAMA_3_70B,
    ],

    TASK_CODE: [
        QWEN_32B,
        LLAMA_3_70B,
        DEEPSEEK_CHAT,
        MISTRAL_SMALL,
    ],

    TASK_VISION: [
        GEMMA_4,
        LLAMA_3_70B,
    ],

    TASK_CHEAP: [
        MISTRAL_SMALL,
        DEEPSEEK_CHAT,
        QWEN_32B,
        GEMMA_4,
        LLAMA_3_70B,
    ],
}


# ============================================================================
# TASK ALLOWED MODELS
# ============================================================================

TASK_ALLOWED_MODELS: Final[
    dict[str, tuple[str, ...]]
] = {
    task: tuple(models)
    for task, models in TASK_FALLBACK_MODELS.items()
}


# ============================================================================
# GENERATION DEFAULTS
# ============================================================================

DEFAULT_TEMPERATURE: Final[float] = 0.7

DEFAULT_MAX_TOKENS: Final[int] = 1024

DEFAULT_TOP_P: Final[float] = 0.95


# ============================================================================
# TASK TOKEN LIMITS
# ============================================================================

FAST_MAX_TOKENS: Final[int] = 512

CHAT_MAX_TOKENS: Final[int] = 1024

REASONING_MAX_TOKENS: Final[int] = 1536

CODE_MAX_TOKENS: Final[int] = 1536

VISION_MAX_TOKENS: Final[int] = 1024

CHEAP_MAX_TOKENS: Final[int] = 512


TASK_MAX_TOKENS: Final[dict[str, int]] = {
    TASK_CHAT: CHAT_MAX_TOKENS,
    TASK_REASONING: REASONING_MAX_TOKENS,
    TASK_FAST: FAST_MAX_TOKENS,
    TASK_CODE: CODE_MAX_TOKENS,
    TASK_VISION: VISION_MAX_TOKENS,
    TASK_CHEAP: CHEAP_MAX_TOKENS,
}


# ============================================================================
# TASK TEMPERATURES
# ============================================================================

TASK_TEMPERATURES: Final[dict[str, float]] = {
    TASK_CHAT: 0.7,
    TASK_REASONING: 0.2,
    TASK_FAST: 0.0,
    TASK_CODE: 0.2,
    TASK_VISION: 0.3,
    TASK_CHEAP: 0.4,
}


# ============================================================================
# RETRY STATUS POLICY
# ============================================================================

RETRYABLE_STATUS_CODES: Final[
    frozenset[int]
] = frozenset(
    {
        408,
        429,
        500,
        502,
        503,
        504,
    }
)


NON_RETRYABLE_STATUS_CODES: Final[
    frozenset[int]
] = frozenset(
    {
        400,
        401,
        403,
        404,
    }
)


CREDIT_EXHAUSTION_STATUS_CODES: Final[
    frozenset[int]
] = frozenset(
    {
        402,
    }
)


# ============================================================================
# RETRY / FALLBACK DEFAULTS
# ============================================================================

DEFAULT_TIMEOUT: Final[int] = 60

DEFAULT_RETRIES: Final[int] = 2

MAX_FALLBACK_ATTEMPTS: Final[int] = (
    len(DEFAULT_MODELS)
)


# ============================================================================
# CONTEXT
# ============================================================================

DEFAULT_CONTEXT_BUDGET: Final[int] = 12_000

DEFAULT_CHARS_PER_TOKEN: Final[int] = 4

MIN_INPUT_TOKENS: Final[int] = 256

MIN_MESSAGE_TOKENS: Final[int] = 32

TRUNCATION_MARKER: Final[str] = (
    "\n\n[...context truncated...]\n\n"
)


# ============================================================================
# VALIDATION DEFAULTS
# ============================================================================

DEFAULT_TASK: Final[str] = TASK_CHAT


# ============================================================================
# MODEL POLICY HELPERS
# ============================================================================

ALL_CONFIGURED_MODELS: Final[
    tuple[str, ...]
] = tuple(
    dict.fromkeys(
        model
        for models in TASK_FALLBACK_MODELS.values()
        for model in models
    )
)


# ============================================================================
# COMPATIBILITY ALIASES
# ============================================================================

DEFAULT_MODEL_ORDER: Final[
    tuple[str, ...]
] = DEFAULT_MODELS

MODEL_FALLBACKS: Final[
    dict[str, list[str]]
] = TASK_FALLBACK_MODELS


TASK_POLICY_KEYS: Final[
    tuple[str, ...]
] = SUPPORTED_TASKS