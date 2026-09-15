"""
Query Complexity Estimator

Estimates how difficult a query is to answer and predicts
resources required for retrieval and reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import List


class ComplexityLevel(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class ComplexityEstimate:
    level: ComplexityLevel
    score: float

    estimated_steps: int

    requires_search: bool
    requires_reasoning: bool
    requires_multi_hop: bool
    requires_code: bool

    explanation: List[str]


class ComplexityEstimator:

    QUESTION_WORDS = {
        "why",
        "how",
        "compare",
        "difference",
        "advantages",
        "disadvantages",
        "analyze",
        "explain",
        "evaluate",
        "design",
        "architecture",
        "research",
        "strategy",
    }

    CODE_KEYWORDS = {
        "python",
        "javascript",
        "code",
        "implement",
        "build",
        "fastapi",
        "react",
        "debug",
        "api",
    }

    MULTI_HOP_WORDS = {
        "and",
        "or",
        "while",
        "versus",
        "vs",
        "then",
        "also",
        "relationship",
    }

    def estimate(self, query: str) -> ComplexityEstimate:

        query_lower = query.lower()

        score = 0
        reasons = []

        # ------------------------
        # Length
        # ------------------------

        words = query_lower.split()

        if len(words) > 10:
            score += 10
            reasons.append("Long query")

        if len(words) > 25:
            score += 15
            reasons.append("Very long query")

        # ------------------------
        # Question complexity
        # ------------------------

        matches = [
            w
            for w in self.QUESTION_WORDS
            if w in query_lower
        ]

        score += len(matches) * 8

        if matches:
            reasons.append("Analytical question")

        # ------------------------
        # Multi-hop
        # ------------------------

        multi = any(
            word in query_lower
            for word in self.MULTI_HOP_WORDS
        )

        if multi:
            score += 15
            reasons.append("Multi-hop reasoning")

        # ------------------------
        # Code
        # ------------------------

        code = any(
            c in query_lower
            for c in self.CODE_KEYWORDS
        )

        if code:
            score += 20
            reasons.append("Programming task")

        # ------------------------
        # Numbers / equations
        # ------------------------

        if re.search(r"\d", query):
            score += 5

        # ------------------------
        # Search detection
        # ------------------------

        search = any(
            word in query_lower
            for word in [
                "latest",
                "current",
                "today",
                "news",
                "recent",
            ]
        )

        if search:
            score += 10
            reasons.append("Needs external knowledge")

        # ------------------------
        # Normalize
        # ------------------------

        score = min(score, 100)

        if score < 20:
            level = ComplexityLevel.SIMPLE
            steps = 1

        elif score < 45:
            level = ComplexityLevel.MODERATE
            steps = 2

        elif score < 70:
            level = ComplexityLevel.COMPLEX
            steps = 4

        else:
            level = ComplexityLevel.VERY_COMPLEX
            steps = 6

        return ComplexityEstimate(
            level=level,
            score=score,
            estimated_steps=steps,
            requires_search=search,
            requires_reasoning=level
            != ComplexityLevel.SIMPLE,
            requires_multi_hop=multi,
            requires_code=code,
            explanation=reasons,
        )