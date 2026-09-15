"""
Text utility functions.

Used throughout:
- ingestion
- chunking
- indexing
- retrieval
- embeddings
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter


WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    """
    Collapse repeated whitespace.
    """

    return WHITESPACE_RE.sub(" ", text).strip()


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters.
    """

    return unicodedata.normalize("NFKC", text)


def clean_text(text: str) -> str:
    """
    General-purpose text cleaning.
    """

    text = normalize_unicode(text)
    text = normalize_whitespace(text)

    return text


def remove_control_characters(text: str) -> str:
    """
    Remove non-printable characters.
    """

    return "".join(
        c
        for c in text
        if c.isprintable()
    )


def truncate(
    text: str,
    max_length: int,
    suffix: str = "...",
) -> str:
    """
    Truncate text.
    """

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def word_count(text: str) -> int:
    """
    Count words.
    """

    return len(text.split())


def character_count(text: str) -> int:
    """
    Count characters.
    """

    return len(text)


def unique_words(text: str) -> set[str]:
    """
    Return unique words.
    """

    return set(text.lower().split())


def most_common_words(
    text: str,
    n: int = 10,
) -> list[tuple[str, int]]:
    """
    Return most frequent words.
    """

    counts = Counter(text.lower().split())

    return counts.most_common(n)


def sentences(text: str) -> list[str]:
    """
    Basic sentence splitter.
    """

    parts = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [p for p in parts if p]


def lines(text: str) -> list[str]:
    """
    Return non-empty lines.
    """

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def paragraphs(text: str) -> list[str]:
    """
    Split text into paragraphs.
    """

    return [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]


def contains_url(text: str) -> bool:
    """
    Detect URLs.
    """

    return bool(
        re.search(
            r"https?://\S+|www\.\S+",
            text,
        )
    )


def contains_email(text: str) -> bool:
    """
    Detect email addresses.
    """

    return bool(
        re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text,
        )
    )