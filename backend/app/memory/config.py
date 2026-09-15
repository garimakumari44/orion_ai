"""
Configuration for the memory subsystem.
"""

from dataclasses import dataclass

from .constants import (
    DEFAULT_EPISODE_WINDOW,
    DEFAULT_MAX_CONTEXT_TOKENS,
    DEFAULT_MAX_WORKING_MEMORY,
    DEFAULT_MEMORY_DECAY_DAYS,
    DEFAULT_SIMILARITY_THRESHOLD,
)


@dataclass(slots=True)
class MemoryConfig:
    """
    Global configuration for memory management.
    """

    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD

    working_memory_capacity: int = DEFAULT_MAX_WORKING_MEMORY

    episode_window: int = DEFAULT_EPISODE_WINDOW

    decay_days: int = DEFAULT_MEMORY_DECAY_DAYS

    max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS

    enable_decay: bool = True

    enable_deduplication: bool = True

    enable_summarization: bool = True

    enable_semantic_search: bool = True

    enable_research_memory: bool = True

    auto_consolidation: bool = True

    persistence_enabled: bool = True