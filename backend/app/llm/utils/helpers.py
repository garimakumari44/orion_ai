"""
General helper utilities.

Used across:
- LLM providers
- Agents
- Tools
- RAG pipeline
- Evaluation
- Observability
"""

from __future__ import annotations

import hashlib
import uuid
import re
from typing import Any, Dict, Iterable


def generate_id(prefix: str = "") -> str:
    """
    Generate unique identifier.

    Example:
        request_7d91f3a2
    """

    uid = uuid.uuid4().hex[:8]

    if prefix:
        return f"{prefix}_{uid}"

    return uid


def hash_text(text: str) -> str:
    """
    Generate deterministic hash.

    Useful for:
    - Cache keys
    - Prompt caching
    - Deduplication
    """

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def normalize_text(text: str) -> str:
    """
    Normalize text input.

    Removes:
    - Extra spaces
    - Strange whitespace
    - Leading/trailing spaces
    """

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def safe_get(
    data: Dict[str, Any],
    key: str,
    default: Any = None,
):
    """
    Safe dictionary access.

    Avoids KeyError.
    """

    return data.get(
        key,
        default,
    )


def chunk_list(
    items: list[Any],
    size: int,
) -> list[list[Any]]:
    """
    Split list into chunks.

    Example:
        [1,2,3,4,5]
        size=2

        [
          [1,2],
          [3,4],
          [5]
        ]
    """

    return [
        items[i:i + size]
        for i in range(
            0,
            len(items),
            size
        )
    ]


def flatten(
    items: Iterable[list[Any]],
) -> list[Any]:
    """
    Flatten nested lists.
    """

    return [
        item
        for group in items
        for item in group
    ]


def is_empty(value: Any) -> bool:
    """
    Check empty values.
    """

    return (
        value is None
        or value == ""
        or value == []
        or value == {}
    )


def mask_secret(
    value: str,
    visible_chars: int = 4,
) -> str:
    """
    Hide API keys/secrets.

    Example:

    sk-123456789

    becomes:

    sk-12********
    """

    if len(value) <= visible_chars:
        return "*" * len(value)

    return (
        value[:visible_chars]
        +
        "*" * (len(value)-visible_chars)
    )


def merge_dicts(
    *dicts: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merge dictionaries.

    Later dictionaries override earlier ones.
    """

    result = {}

    for item in dicts:
        result.update(item)

    return result


def retryable_error(
    exception: Exception,
    retry_keywords: list[str],
) -> bool:
    """
    Determine if error is retryable.

    Useful for:
    - Rate limits
    - Temporary failures
    """

    message = str(exception).lower()

    return any(
        keyword.lower()
        in message
        for keyword in retry_keywords
    )