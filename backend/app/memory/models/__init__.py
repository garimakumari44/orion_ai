"""
Memory data models.

This package contains the core models used throughout the memory
subsystem, including generic memories, episodic memories, user
preferences, and research memories.
"""

from .memory import (
    Memory,
    MemoryContent,
    MemoryMetadata,
    MemorySource,
    MemoryType,
)

from .episode import (
    Episode,
    EpisodeStatus,
    EpisodeStep,
)

from .preference import (
    Preference,
    PreferenceScope,
    PreferenceType,
)

from .research import (
    ResearchFinding,
    ResearchMemory,
    ResearchSource,
    ResearchStatus,
)

__all__ = [
    # ------------------------------------------------------------------
    # Core Memory
    # ------------------------------------------------------------------
    "Memory",
    "MemoryContent",
    "MemoryMetadata",
    "MemorySource",
    "MemoryType",

    # ------------------------------------------------------------------
    # Episodic Memory
    # ------------------------------------------------------------------
    "Episode",
    "EpisodeStep",
    "EpisodeStatus",

    # ------------------------------------------------------------------
    # User Preferences
    # ------------------------------------------------------------------
    "Preference",
    "PreferenceType",
    "PreferenceScope",

    # ------------------------------------------------------------------
    # Research Memory
    # ------------------------------------------------------------------
    "ResearchMemory",
    "ResearchFinding",
    "ResearchSource",
    "ResearchStatus",
]