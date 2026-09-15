"""
Temporal enrichment.

Extracts temporal metadata from documents to support:

- Temporal search
- Timeline generation
- Time-aware retrieval
- Freshness ranking
- Analytics
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------


@dataclass(slots=True)
class TemporalResult:
    """Temporal metadata extracted from a document."""

    extracted_dates: list[datetime] = field(default_factory=list)

    earliest_date: Optional[datetime] = None
    latest_date: Optional[datetime] = None

    relative_expressions: list[str] = field(default_factory=list)

    document_created_at: Optional[datetime] = None
    document_updated_at: Optional[datetime] = None

    recency_score: float = 0.0

    contains_future_dates: bool = False


# ---------------------------------------------------------------------
# Temporal Enricher
# ---------------------------------------------------------------------


class TemporalEnricher:
    """
    Rule-based temporal metadata extractor.
    """

    DATE_PATTERNS = [

        # 2025-06-15
        re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),

        # 15/06/2025
        re.compile(r"\b\d{2}/\d{2}/\d{4}\b"),

        # 15-06-2025
        re.compile(r"\b\d{2}-\d{2}-\d{4}\b"),
    ]

    RELATIVE_PATTERNS = [
        "today",
        "yesterday",
        "tomorrow",
        "last week",
        "last month",
        "last year",
        "this week",
        "this month",
        "this year",
        "next week",
        "next month",
        "next year",
    ]

    def enrich(
        self,
        text: str,
        *,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> TemporalResult:
        """
        Extract temporal metadata from text.
        """

        text_lower = text.lower()

        dates = self._extract_dates(text)

        earliest = min(dates) if dates else None
        latest = max(dates) if dates else None

        relatives = [
            expr
            for expr in self.RELATIVE_PATTERNS
            if expr in text_lower
        ]

        now = datetime.now(timezone.utc)

        contains_future = any(
            dt > now
            for dt in dates
        )

        recency = self._calculate_recency(
            updated_at or created_at
        )

        return TemporalResult(
            extracted_dates=dates,
            earliest_date=earliest,
            latest_date=latest,
            relative_expressions=relatives,
            document_created_at=created_at,
            document_updated_at=updated_at,
            recency_score=recency,
            contains_future_dates=contains_future,
        )

    # ---------------------------------------------------------

    def _extract_dates(
        self,
        text: str,
    ) -> list[datetime]:

        extracted = []

        for pattern in self.DATE_PATTERNS:

            for match in pattern.findall(text):

                parsed = self._parse_date(match)

                if parsed:
                    extracted.append(parsed)

        return sorted(set(extracted))

    # ---------------------------------------------------------

    @staticmethod
    def _parse_date(
        value: str,
    ) -> Optional[datetime]:

        formats = (
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
        )

        for fmt in formats:

            try:
                return datetime.strptime(
                    value,
                    fmt,
                ).replace(
                    tzinfo=timezone.utc
                )

            except ValueError:
                pass

        return None

    # ---------------------------------------------------------

    @staticmethod
    def _calculate_recency(
        timestamp: datetime | None,
    ) -> float:
        """
        Returns a freshness score between 0 and 1.
        """

        if timestamp is None:
            return 0.0

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        age_days = (now - timestamp).days

        if age_days <= 0:
            return 1.0

        return 1 / (1 + age_days / 30)


# ---------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------


def enrich_temporal(
    text: str,
    *,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> TemporalResult:
    """
    Convenience wrapper.
    """

    return TemporalEnricher().enrich(
        text=text,
        created_at=created_at,
        updated_at=updated_at,
    )