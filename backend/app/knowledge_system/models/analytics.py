"""
Analytics enrichment.

Computes useful document statistics that can later be used for:

- Retrieval ranking
- Quality scoring
- Monitoring
- Dashboard analytics
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------


@dataclass(slots=True)
class DocumentAnalytics:
    word_count: int
    sentence_count: int
    paragraph_count: int

    average_sentence_length: float
    average_word_length: float

    unique_words: int
    lexical_diversity: float

    estimated_reading_minutes: float

    top_keywords: list[str]

    numeric_count: int
    url_count: int
    email_count: int

    language_confidence: float = 1.0


# ---------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------


class AnalyticsEnricher:
    """
    Compute descriptive statistics for a document.
    """

    URL_RE = re.compile(r"https?://\S+")

    EMAIL_RE = re.compile(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")

    SENTENCE_RE = re.compile(r"[.!?]+")

    STOPWORDS = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "to",
        "of",
        "and",
        "in",
        "on",
        "for",
        "at",
        "that",
        "this",
        "it",
        "with",
        "as",
        "by",
        "or",
        "from",
    }

    def analyze(self, text: str) -> DocumentAnalytics:
        text = text.strip()

        words = WORD_RE.findall(text)

        word_count = len(words)

        sentence_count = max(
            1,
            len(self.SENTENCE_RE.findall(text)),
        )

        paragraphs = [
            p for p in text.split("\n\n")
            if p.strip()
        ]

        paragraph_count = max(1, len(paragraphs))

        avg_sentence = (
            word_count / sentence_count
            if sentence_count
            else 0
        )

        avg_word = (
            sum(len(w) for w in words) / word_count
            if word_count
            else 0
        )

        lowered = [w.lower() for w in words]

        unique = len(set(lowered))

        diversity = (
            unique / word_count
            if word_count
            else 0
        )

        reading = word_count / 200

        keywords = self._keywords(lowered)

        return DocumentAnalytics(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            average_sentence_length=round(avg_sentence, 2),
            average_word_length=round(avg_word, 2),
            unique_words=unique,
            lexical_diversity=round(diversity, 3),
            estimated_reading_minutes=round(reading, 2),
            top_keywords=keywords,
            numeric_count=len(
                self.NUMBER_RE.findall(text)
            ),
            url_count=len(
                self.URL_RE.findall(text)
            ),
            email_count=len(
                self.EMAIL_RE.findall(text)
            ),
        )

    # -------------------------------------------------------------

    def _keywords(
        self,
        words: list[str],
        top_k: int = 15,
    ) -> list[str]:

        filtered = [
            w
            for w in words
            if len(w) > 2
            and w not in self.STOPWORDS
        ]

        counter = Counter(filtered)

        return [
            word
            for word, _ in counter.most_common(top_k)
        ]


# ---------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------


def analyze_document(text: str) -> dict[str, Any]:
    """
    Convenience wrapper.
    """

    analytics = AnalyticsEnricher().analyze(text)

    return analytics.__dict__