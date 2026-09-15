"""
Claim Extraction

Extracts factual claims from responses so they can later be verified
against retrieved evidence.

This module intentionally supports both rule-based extraction and
future LLM-powered extraction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Claim:
    """
    Represents one factual claim.
    """

    text: str
    sentence: str

    confidence: float = 0.5

    entities: List[str] = field(default_factory=list)

    numbers: List[str] = field(default_factory=list)

    citations: List[str] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)


class ClaimExtractor:
    """
    Lightweight claim extractor.

    This implementation uses heuristics and is intended
    to be replaced or augmented by an LLM later.
    """

    ENTITY_PATTERN = re.compile(r"\b[A-Z][a-zA-Z]+\b")

    NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")

    CITATION_PATTERN = re.compile(r"\[(\d+)\]")

    def split_sentences(self, text: str) -> List[str]:
        """
        Basic sentence splitter.
        """

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        return [s.strip() for s in sentences if s.strip()]

    def looks_like_claim(self, sentence: str) -> bool:
        """
        Heuristic claim detector.
        """

        if len(sentence.split()) < 5:
            return False

        keywords = [
            "is",
            "are",
            "was",
            "were",
            "has",
            "have",
            "contains",
            "causes",
            "means",
            "shows",
            "states",
            "reported",
            "according",
            "found",
        ]

        lower = sentence.lower()

        return any(word in lower for word in keywords)

    def extract(self, text: str) -> List[Claim]:
        """
        Extract factual claims.
        """

        claims = []

        for sentence in self.split_sentences(text):

            if not self.looks_like_claim(sentence):
                continue

            entities = self.ENTITY_PATTERN.findall(sentence)

            numbers = self.NUMBER_PATTERN.findall(sentence)

            citations = self.CITATION_PATTERN.findall(sentence)

            confidence = 0.5

            if numbers:
                confidence += 0.1

            if entities:
                confidence += 0.1

            if citations:
                confidence += 0.2

            confidence = min(confidence, 1.0)

            claims.append(
                Claim(
                    text=sentence,
                    sentence=sentence,
                    confidence=confidence,
                    entities=entities,
                    numbers=numbers,
                    citations=citations,
                )
            )

        return claims


_default = ClaimExtractor()


def extract_claims(text: str) -> List[Claim]:
    """
    Convenience wrapper.
    """

    return _default.extract(text)