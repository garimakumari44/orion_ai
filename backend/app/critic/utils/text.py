"""
text.py

Text processing utilities used across evaluation pipeline.
"""

import re
from typing import List


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.

    Operations:
    - Lowercase
    - Remove extra whitespace
    - Remove surrounding spaces
    """

    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_markdown(text: str) -> str:
    """
    Remove common markdown formatting.

    Example:
        **hello** -> hello
        # Title -> Title
    """

    if not text:
        return ""

    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)

    return text.strip()


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    """

    if not text:
        return ""

    return re.sub(
        r"https?://\S+",
        "",
        text
    ).strip()


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences.

    Used for:
    - claim extraction
    - hallucination detection
    - citation matching
    """

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def extract_words(text: str) -> List[str]:
    """
    Extract words from text.
    """

    if not text:
        return []

    return re.findall(
        r"\b[a-zA-Z]+\b",
        text.lower()
    )


def word_count(text: str) -> int:
    """
    Count words.
    """

    return len(extract_words(text))


def truncate_text(
    text: str,
    max_length: int = 1000
) -> str:
    """
    Limit text size.
    """

    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


def contains_keyword(
    text: str,
    keyword: str
) -> bool:
    """
    Check keyword existence.
    """

    return keyword.lower() in text.lower()


def remove_empty_lines(text: str) -> str:
    """
    Remove blank lines.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)