"""
Taxonomy enrichment.

Assigns hierarchical categories (taxonomy) to documents
using configurable keyword-based rules.

Example:
Technology
├── Artificial Intelligence
│   ├── Machine Learning
│   ├── Deep Learning
│   └── LLMs
├── Software Engineering
└── Cloud Computing
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------


@dataclass(slots=True)
class TaxonomyNode:
    """Represents one taxonomy match."""

    category: str
    confidence: float
    matched_keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TaxonomyResult:
    """Collection of matched taxonomy nodes."""

    categories: list[TaxonomyNode] = field(default_factory=list)

    @property
    def primary_category(self) -> str | None:
        if not self.categories:
            return None
        return max(
            self.categories,
            key=lambda node: node.confidence,
        ).category


# ---------------------------------------------------------------------
# Taxonomy Enricher
# ---------------------------------------------------------------------


class TaxonomyEnricher:
    """
    Rule-based taxonomy classifier.

    Categories can easily be extended by modifying
    the TAXONOMY dictionary.
    """

    TAXONOMY: dict[str, set[str]] = {
        "Artificial Intelligence": {
            "ai",
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "llm",
            "gpt",
            "embedding",
            "transformer",
            "rag",
        },
        "Software Engineering": {
            "python",
            "java",
            "javascript",
            "typescript",
            "api",
            "backend",
            "frontend",
            "microservice",
            "docker",
            "kubernetes",
        },
        "Databases": {
            "postgres",
            "mysql",
            "mongodb",
            "redis",
            "neo4j",
            "qdrant",
            "database",
            "sql",
        },
        "Cloud Computing": {
            "aws",
            "azure",
            "gcp",
            "cloud",
            "serverless",
            "lambda",
            "s3",
        },
        "Cybersecurity": {
            "security",
            "authentication",
            "authorization",
            "oauth",
            "jwt",
            "encryption",
            "attack",
            "vulnerability",
        },
        "Data Science": {
            "numpy",
            "pandas",
            "statistics",
            "visualization",
            "analytics",
            "regression",
            "classification",
        },
    }

    def classify(self, text: str) -> TaxonomyResult:
        """
        Classify a document into one or more categories.
        """

        text = text.lower()

        matches: list[TaxonomyNode] = []

        for category, keywords in self.TAXONOMY.items():

            matched = [
                keyword
                for keyword in keywords
                if keyword in text
            ]

            if not matched:
                continue

            confidence = len(matched) / len(keywords)

            matches.append(
                TaxonomyNode(
                    category=category,
                    confidence=round(confidence, 3),
                    matched_keywords=matched,
                )
            )

        matches.sort(
            key=lambda x: x.confidence,
            reverse=True,
        )

        return TaxonomyResult(matches)

    def add_category(
        self,
        name: str,
        keywords: Iterable[str],
    ) -> None:
        """
        Register a new taxonomy category.
        """

        self.TAXONOMY[name] = {
            keyword.lower()
            for keyword in keywords
        }

    def remove_category(self, name: str) -> None:
        """
        Remove an existing taxonomy category.
        """

        self.TAXONOMY.pop(name, None)


# ---------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------


def classify_document(text: str) -> TaxonomyResult:
    """
    Classify a document using the default taxonomy.
    """

    return TaxonomyEnricher().classify(text)