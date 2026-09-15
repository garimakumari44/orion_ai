"""
planner/query_analyzer.py

Analyzes user queries before planning retrieval.

Pipeline
--------
Raw Query
    ↓
Normalization
    ↓
Tokenization
    ↓
Entity Extraction
    ↓
Intent Classification
    ↓
Complexity Analysis
    ↓
Structured QueryAnalysis
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from .intent_classifier import (
    IntentClassifier,
    IntentResult,
)


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------


@dataclass(slots=True)
class QueryAnalysis:
    original_query: str
    normalized_query: str

    tokens: List[str]

    entities: List[str]

    intent: IntentResult

    complexity: str

    is_question: bool

    has_temporal_reference: bool

    metadata: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------
# Query Analyzer
# ---------------------------------------------------------------------


class QueryAnalyzer:
    """
    Performs lightweight NLP analysis of user queries.

    Future versions may integrate:
        - spaCy
        - LLM parsing
        - Named Entity Recognition
        - Semantic parsing
    """

    QUESTION_WORDS = {
        "what",
        "why",
        "how",
        "when",
        "where",
        "who",
        "which",
    }

    TEMPORAL_WORDS = {
        "today",
        "yesterday",
        "tomorrow",
        "latest",
        "recent",
        "current",
        "history",
        "before",
        "after",
        "last",
        "next",
    }

    def __init__(self):
        self.intent_classifier = IntentClassifier()

    # ----------------------------------------------------------

    def analyze(self, query: str) -> QueryAnalysis:
        """
        Analyze a raw user query.
        """

        normalized = self._normalize(query)

        tokens = self._tokenize(normalized)

        entities = self._extract_entities(query)

        intent = self.intent_classifier.classify(normalized)

        complexity = self._estimate_complexity(tokens)

        is_question = self._is_question(normalized)

        temporal = self._contains_temporal(tokens)

        return QueryAnalysis(
            original_query=query,
            normalized_query=normalized,
            tokens=tokens,
            entities=entities,
            intent=intent,
            complexity=complexity,
            is_question=is_question,
            has_temporal_reference=temporal,
        )

    # ----------------------------------------------------------

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ----------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\b[\w\-]+\b", text)

    # ----------------------------------------------------------

    @staticmethod
    def _extract_entities(query: str) -> List[str]:
        """
        Very lightweight entity extraction.

        Current strategy:
        - Consecutive capitalized words

        Future:
            spaCy NER
            LLM extraction
        """

        pattern = r"(?:[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)"

        matches = re.findall(pattern, query)

        return list(dict.fromkeys(matches))

    # ----------------------------------------------------------

    def _estimate_complexity(self, tokens: List[str]) -> str:

        n = len(tokens)

        if n < 5:
            return "simple"

        if n < 15:
            return "medium"

        return "complex"

    # ----------------------------------------------------------

    def _is_question(self, text: str) -> bool:

        if text.endswith("?"):
            return True

        first = text.split()[0] if text.split() else ""

        return first in self.QUESTION_WORDS

    # ----------------------------------------------------------

    def _contains_temporal(self, tokens: List[str]) -> bool:

        return any(token in self.TEMPORAL_WORDS for token in tokens)