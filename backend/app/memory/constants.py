"""
Constants used throughout the memory subsystem.
"""

from enum import Enum


class MemoryStoreType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    RESEARCH = "research"

class MemoryPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DELETED = "deleted"


class RetrievalMode(str, Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


class ImportanceLevel:
    LOW = 0.25
    MEDIUM = 0.50
    HIGH = 0.75
    CRITICAL = 1.00


DEFAULT_TOP_K = 10

DEFAULT_SIMILARITY_THRESHOLD = 0.75

DEFAULT_MAX_WORKING_MEMORY = 50

DEFAULT_EPISODE_WINDOW = 25

DEFAULT_MEMORY_DECAY_DAYS = 90

DEFAULT_MAX_CONTEXT_TOKENS = 8000