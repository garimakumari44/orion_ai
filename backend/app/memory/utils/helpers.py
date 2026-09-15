"""
General helper utilities for the memory system.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone


def generate_memory_id() -> str:
    """
    Generate a unique memory identifier.
    """
    return str(uuid.uuid4())


def current_timestamp() -> datetime:
    """
    Return the current UTC timestamp.
    """
    return datetime.now(timezone.utc)


def normalize_text(text: str) -> str:
    """
    Normalize text before indexing or comparison.
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(
    text: str,
    max_length: int = 500,
) -> str:
    """
    Truncate text while preserving readability.
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - 3].rstrip() + "..."


def safe_float(value: float | int | None, default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: int | float | None, default: int = 0) -> int:
    """
    Safely convert a value to int.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default