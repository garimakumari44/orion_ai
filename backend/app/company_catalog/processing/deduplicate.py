"""
app/company_catalog/processing/deduplicate.py

Company Deduplicator

Finds duplicate company records using canonical identity
and normalized classification-independent identifiers.

Architectural rules
-------------------

- Dictionary-only.
- No SQLAlchemy.
- No AsyncSession.
- No repository access.
- No provider-specific logic.
- Classification is NOT used as a deduplication key.
- CompanyNormalizer owns normalization.
"""

from __future__ import annotations

from typing import Any

from app.company_catalog.processing.normalizer import (
    CompanyNormalizer,
)


class CompanyDeduplicator:
    """
    Deduplicate company dictionaries.

    Matching priority:

        1. CIK
        2. LEI
        3. FIGI
        4. ISIN
        5. Ticker + Exchange
        6. Ticker
        7. Normalized Company Name

    Classification fields such as:

        sector
        industry
        sub_industry

    are deliberately NOT used for identity matching.
    """

    # =========================================================
    # Find Existing
    # =========================================================

    def find_existing(
        self,
        company: dict[str, Any],
        existing_companies: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """
        Find an existing company matching the incoming company.

        Both incoming and existing records are normalized before
        comparison.

        Returns the complete existing dictionary so that downstream
        processing can preserve metadata such as:

            sector
            industry
            sub_industry
            website
            description
        """

        if not isinstance(company, dict):
            raise TypeError(
                "company must be a dictionary."
            )

        if not isinstance(existing_companies, list):
            raise TypeError(
                "existing_companies must be a list."
            )

        incoming = CompanyNormalizer.normalize(
            dict(company)
        )

        for existing in existing_companies:

            if not isinstance(existing, dict):
                continue

            candidate = CompanyNormalizer.normalize(
                dict(existing)
            )

            # -------------------------------------------------
            # CIK
            # -------------------------------------------------

            if self._identifier_matches(
                incoming.get("cik"),
                candidate.get("cik"),
            ):
                return existing

            # -------------------------------------------------
            # LEI
            # -------------------------------------------------

            if self._identifier_matches(
                incoming.get("lei"),
                candidate.get("lei"),
            ):
                return existing

            # -------------------------------------------------
            # FIGI
            # -------------------------------------------------

            if self._identifier_matches(
                incoming.get("figi"),
                candidate.get("figi"),
            ):
                return existing

            # -------------------------------------------------
            # ISIN
            # -------------------------------------------------

            if self._identifier_matches(
                incoming.get("isin"),
                candidate.get("isin"),
            ):
                return existing

            # -------------------------------------------------
            # Ticker + Exchange
            # -------------------------------------------------

            if (
                self._ticker_matches(
                    incoming.get("ticker"),
                    candidate.get("ticker"),
                )
                and self._text_matches(
                    incoming.get("exchange"),
                    candidate.get("exchange"),
                )
            ):
                return existing

            # -------------------------------------------------
            # Ticker
            # -------------------------------------------------

            if self._ticker_matches(
                incoming.get("ticker"),
                candidate.get("ticker"),
            ):
                return existing

            # -------------------------------------------------
            # Normalized Name
            # -------------------------------------------------

            if (
                self._text_matches(
                    incoming.get("normalized_name"),
                    candidate.get("normalized_name"),
                )
            ):
                return existing

        return None

    # =========================================================
    # Deduplicate List
    # =========================================================

    def deduplicate(
        self,
        companies: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate companies from a list.

        The first occurrence is retained.
        """

        if not isinstance(companies, list):
            raise TypeError(
                "companies must be a list."
            )

        unique: list[dict[str, Any]] = []

        for company in companies:

            if not isinstance(company, dict):
                continue

            duplicate = self.find_existing(
                company,
                unique,
            )

            if duplicate is None:
                unique.append(company)

        return unique

    # =========================================================
    # Identifier Matching
    # =========================================================

    @staticmethod
    def _identifier_matches(
        left: Any,
        right: Any,
    ) -> bool:
        """
        Compare regulatory identifiers safely.

        Empty values never match.
        """

        if left is None or right is None:
            return False

        left_value = str(left).strip().upper()
        right_value = str(right).strip().upper()

        if not left_value or not right_value:
            return False

        return left_value == right_value

    # =========================================================
    # Ticker Matching
    # =========================================================

    @staticmethod
    def _ticker_matches(
        left: Any,
        right: Any,
    ) -> bool:
        """
        Compare stock tickers case-insensitively.
        """

        if left is None or right is None:
            return False

        left_value = str(left).strip().upper()
        right_value = str(right).strip().upper()

        if not left_value or not right_value:
            return False

        return left_value == right_value

    # =========================================================
    # Text Matching
    # =========================================================

    @staticmethod
    def _text_matches(
        left: Any,
        right: Any,
    ) -> bool:
        """
        Compare normalized text values.
        """

        if left is None or right is None:
            return False

        left_value = str(left).strip().lower()
        right_value = str(right).strip().lower()

        if not left_value or not right_value:
            return False

        return left_value == right_value