"""
Memory consolidation package.

This package provides utilities for maintaining the quality of the memory
store by identifying duplicate memories, merging related memories,
summarizing historical information, and applying memory decay policies.
"""

from .merger import MemoryMerger
from .deduplication import MemoryDeduplicator
from .summarizer import MemorySummarizer
from .decay import MemoryDecay

__all__ = [
    "MemoryMerger",
    "MemoryDeduplicator",
    "MemorySummarizer",
    "MemoryDecay",
]