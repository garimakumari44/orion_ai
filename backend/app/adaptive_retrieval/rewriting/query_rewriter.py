"""
Query Rewriter

Responsible for improving user queries before retrieval.

Capabilities
------------
- Normalize query
- Expand abbreviations
- Generate retrieval variants
- Remove unnecessary filler words
- Optional LLM-based rewriting
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

@dataclass
class QueryRewriteRequest:
    query: str
    enable_expansion: bool = True
    enable_cleanup: bool = True
    generate_variants: bool = True


@dataclass
class QueryRewriteResult:
    original_query: str
    rewritten_query: str
    variants: List[str] = field(default_factory=list)


# ---------------------------------------------------------
# Rewriter
# ---------------------------------------------------------

class QueryRewriter:

    STOP_WORDS = {
        "please",
        "can",
        "could",
        "would",
        "kindly",
        "tell",
        "me",
        "about",
    }

    ABBREVIATIONS = {
        "llm": "large language model",
        "rag": "retrieval augmented generation",
        "gpu": "graphics processing unit",
        "cpu": "central processing unit",
        "nlp": "natural language processing",
        "ml": "machine learning",
        "ai": "artificial intelligence",
    }

    def rewrite(
        self,
        request: QueryRewriteRequest,
    ) -> QueryRewriteResult:

        query = request.query.strip()

        if request.enable_cleanup:
            query = self._cleanup(query)

        if request.enable_expansion:
            query = self._expand(query)

        variants = []

        if request.generate_variants:
            variants = self._variants(query)

        return QueryRewriteResult(
            original_query=request.query,
            rewritten_query=query,
            variants=variants,
        )

    # -----------------------------------------------------

    def _cleanup(self, query: str) -> str:

        words = []

        for token in query.split():

            if token.lower() not in self.STOP_WORDS:
                words.append(token)

        query = " ".join(words)

        query = re.sub(r"\s+", " ", query)

        return query.strip()

    # -----------------------------------------------------

    def _expand(self, query: str) -> str:

        tokens = []

        for token in query.split():

            key = token.lower()

            if key in self.ABBREVIATIONS:
                tokens.append(self.ABBREVIATIONS[key])
            else:
                tokens.append(token)

        return " ".join(tokens)

    # -----------------------------------------------------

    def _variants(self, query: str) -> List[str]:

        variants = []

        variants.append(query)

        variants.append(query.lower())

        variants.append(query.replace("-", " "))

        variants = list(dict.fromkeys(variants))

        return variants