"""
Formatting helpers used throughout the platform.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def pretty_json(data: Any) -> str:
    """
    Pretty print JSON.
    """
    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def compact_json(data: Any) -> str:
    """
    Compact JSON.
    """
    return json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def format_duration(seconds: float) -> str:
    """
    Human-readable duration.

    Example:
        0.5 -> 500 ms
        3.2 -> 3.20 s
    """

    if seconds < 1:
        return f"{seconds*1000:.0f} ms"

    if seconds < 60:
        return f"{seconds:.2f} s"

    minutes = int(seconds // 60)
    remaining = seconds % 60

    return f"{minutes}m {remaining:.1f}s"


def format_number(value: float) -> str:
    """
    Human-friendly large numbers.
    """

    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"

    if value >= 1_000:
        return f"{value/1_000:.2f}K"

    return str(value)


def utc_timestamp() -> str:
    """
    ISO UTC timestamp.
    """

    return datetime.utcnow().isoformat() + "Z"


def truncate(text: str, length: int = 200) -> str:
    """
    Truncate text safely.
    """

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


def separator(length: int = 60, char: str = "-") -> str:
    """
    Create separator line.
    """

    return char * length


def title(text: str) -> str:
    """
    Nicely formatted title.
    """

    return text.replace("_", " ").title()


def indent(text: str, spaces: int = 4) -> str:
    """
    Indent multiline text.
    """

    prefix = " " * spaces
    return "\n".join(prefix + line for line in text.splitlines())


def markdown_code(
    code: str,
    language: str = "",
) -> str:
    """
    Wrap code in markdown block.
    """

    return f"```{language}\n{code}\n```"