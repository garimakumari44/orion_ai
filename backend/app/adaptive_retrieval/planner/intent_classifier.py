"""
planner/intent_classifier.py

Intent classification for adaptive retrieval.

Responsibilities
----------------
- Detect retrieval intent
- Assign confidence
- Support multiple intents
- Provide routing metadata

This classifier is intentionally lightweight.
It can later be replaced with an LLM or Transformer model
without changing downstream APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


# ---------------------------------------------------------------------
# Intent Types
# ---------------------------------------------------------------------


class RetrievalIntent(str, Enum):
    FACT = "fact"
    EXPLANATION = "explanation"
    SUMMARY = "summary"
    COMPARISON = "comparison"
    LIST = "list"
    PROCEDURE = "procedure"
    DEFINITION = "definition"
    REASONING = "reasoning"
    TEMPORAL = "temporal"
    ENTITY_LOOKUP = "entity_lookup"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------


@dataclass(slots=True)
class IntentResult:
    primary: RetrievalIntent

    secondary: List[RetrievalIntent] = field(default_factory=list)

    confidence: float = 0.0

    matched_keywords: List[str] = field(default_factory=list)

    metadata: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------
# Intent Classifier
# ---------------------------------------------------------------------


class IntentClassifier:
    """
    Lightweight rule-based classifier.

    Replace this class with an embedding model or LLM later
    while preserving its interface.
    """

    INTENT_KEYWORDS: Dict[RetrievalIntent, Set[str]] = {
        RetrievalIntent.DEFINITION: {
            "what is",
            "define",
            "meaning",
            "definition",
        },
        RetrievalIntent.EXPLANATION: {
            "why",
            "explain",
            "how does",
            "how do",
            "describe",
        },
        RetrievalIntent.SUMMARY: {
            "summary",
            "summarize",
            "overview",
            "brief",
        },
        RetrievalIntent.COMPARISON: {
            "difference",
            "compare",
            "vs",
            "versus",
        },
        RetrievalIntent.PROCEDURE: {
            "steps",
            "procedure",
            "guide",
            "tutorial",
            "implement",
            "build",
        },
        RetrievalIntent.LIST: {
            "list",
            "examples",
            "top",
            "best",
            "all",
        },
        RetrievalIntent.TEMPORAL: {
            "history",
            "timeline",
            "latest",
            "recent",
            "before",
            "after",
        },
        RetrievalIntent.REASONING: {
            "analyze",
            "analysis",
            "reason",
            "evaluate",
            "tradeoff",
        },
    }

    def classify(self, query: str) -> IntentResult:
        """
        Classify query intent.
        """

        text = query.lower()

        scores: Dict[RetrievalIntent, int] = {}
        matched: List[str] = []

        for intent, keywords in self.INTENT_KEYWORDS.items():

            score = 0

            for keyword in keywords:
                if keyword in text:
                    score += 1
                    matched.append(keyword)

            if score:
                scores[intent] = score

        if not scores:
            return IntentResult(
                primary=RetrievalIntent.UNKNOWN,
                confidence=0.15,
            )

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        primary = ranked[0][0]

        secondary = [
            intent
            for intent, _ in ranked[1:]
        ]

        confidence = min(
            0.5 + ranked[0][1] * 0.15,
            0.99,
        )

        return IntentResult(
            primary=primary,
            secondary=secondary,
            confidence=confidence,
            matched_keywords=matched,
        )