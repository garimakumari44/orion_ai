
"""
app/company_catalog/processing/normalizer.py

Company Normalizer
==================

Normalizes raw company/provider data into the canonical
dictionary representation used by the company-processing
pipeline.

Canonical identity fields:

    name
    company_name
    company
    normalized_name
    ticker
    website
    country

Canonical classification fields:

    sector
    industry
    sub_industry

Important architectural rule:

    sector != industry

A sector value must NEVER be used as an industry fallback.

The normalizer is provider-agnostic. It accepts the different
field names commonly returned by company-data providers and
converts them into the canonical company schema.

Canonical pipeline:

    Provider
        |
        v
    CompanyNormalizer
        |
        v
    CompanyValidator
        |
        v
    CompanyDeduplicator
        |
        v
    CompanyProcessingPipeline
        |
        v
    CompanyRepository
        |
        v
    companies table
"""

from __future__ import annotations

import re
from typing import Any


class CompanyNormalizer:
    """
    Normalize company data before validation, deduplication,
    merging, and persistence.

    This class:

    - does not access the database
    - does not access repositories
    - does not call external APIs
    - does not perform LLM analysis
    - does not infer industry from sector
    - does not construct providers

    It only converts provider dictionaries into canonical
    company dictionaries.
    """

    # =====================================================================
    # Name
    # =====================================================================

    @staticmethod
    def normalize_name(
        name: str | None,
    ) -> str | None:
        """
        Normalize a company name.
        """

        if name is None:
            return None

        if not isinstance(name, str):
            name = str(name)

        name = re.sub(
            r"\s+",
            " ",
            name.strip(),
        )

        return name or None

    # =====================================================================
    # Deduplication Name
    # =====================================================================

    @staticmethod
    def normalize_name_for_matching(
        name: str | None,
    ) -> str | None:
        """
        Produce a stable normalized name for matching.
        """

        normalized = CompanyNormalizer.normalize_name(
            name,
        )

        if not normalized:
            return None

        normalized = re.sub(
            r"[^\w\s]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip().lower() or None

    # =====================================================================
    # Ticker
    # =====================================================================

    @staticmethod
    def normalize_ticker(
        ticker: str | None,
    ) -> str | None:
        """
        Normalize a ticker symbol.
        """

        if ticker is None:
            return None

        if not isinstance(ticker, str):
            ticker = str(ticker)

        ticker = ticker.strip().upper()

        return ticker or None

    # =====================================================================
    # Website
    # =====================================================================

    @staticmethod
    def normalize_website(
        url: str | None,
    ) -> str | None:
        """
        Normalize a company website URL.
        """

        if url is None:
            return None

        if not isinstance(url, str):
            url = str(url)

        url = url.strip()

        if not url:
            return None

        if not url.startswith(
            (
                "http://",
                "https://",
            )
        ):
            url = f"https://{url}"

        return url.rstrip("/")

    # =====================================================================
    # Country
    # =====================================================================

    @staticmethod
    def normalize_country(
        country: str | None,
    ) -> str | None:
        """
        Normalize country text.
        """

        if country is None:
            return None

        if not isinstance(country, str):
            country = str(country)

        country = country.strip()

        if not country:
            return None

        return country.title()

    # =====================================================================
    # Generic Text
    # =====================================================================

    @staticmethod
    def normalize_text(
        value: Any,
    ) -> Any:
        """
        Normalize generic text while preserving None.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = re.sub(
            r"\s+",
            " ",
            value.strip(),
        )

        return value or None

    # =====================================================================
    # Meaningful Value
    # =====================================================================

    @staticmethod
    def _meaningful(
        value: Any,
    ) -> bool:
        """
        Return True when a provider value contains useful data.
        """

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True

    # =====================================================================
    # Field Resolution
    # =====================================================================

    @classmethod
    def _resolve_field(
        cls,
        data: dict[str, Any],
        *fields: str,
    ) -> Any:
        """
        Resolve the first meaningful value from flat fields.
        """

        if not isinstance(data, dict):
            return None

        for field in fields:
            if field not in data:
                continue

            value = data.get(field)

            if cls._meaningful(value):
                return value

        return None

    # =====================================================================
    # Nested Classification Containers
    # =====================================================================

    @staticmethod
    def _classification_sources(
        data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Return possible nested classification dictionaries.

        Supported containers include:

            classification
            classifications
            industry_classification
            industryClassification
            metadata
            profile
            company
            details
        """

        if not isinstance(data, dict):
            return []

        sources: list[dict[str, Any]] = []

        for key in (
            "classification",
            "classifications",
            "industry_classification",
            "industryClassification",
            "metadata",
            "profile",
            "company",
            "details",
        ):
            value = data.get(key)

            if isinstance(value, dict):
                sources.append(value)

        return sources

    # =====================================================================
    # Recursive Classification Lookup
    # =====================================================================

    @classmethod
    def _resolve_classification_field(
        cls,
        data: dict[str, Any],
        *fields: str,
    ) -> Any:
        """
        Resolve a classification field from:

            1. top-level fields
            2. nested classification containers

        Each classification dimension is resolved independently.

        IMPORTANT:

            This method does not cross-populate sector,
            industry, or sub-industry.
        """

        value = cls._resolve_field(
            data,
            *fields,
        )

        if value is not None:
            return value

        for source in cls._classification_sources(data):
            value = cls._resolve_field(
                source,
                *fields,
            )

            if value is not None:
                return value

        return None

    # =====================================================================
    # Sector
    # =====================================================================

    @classmethod
    def normalize_sector(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Resolve sector independently.

        Sector is NEVER used to populate industry.
        """

        value = cls._resolve_classification_field(
            data,
            "sector",
            "sector_name",
            "sectorName",
            "sector_description",
            "sectorDescription",
        )

        return cls.normalize_text(value)

    # =====================================================================
    # Industry
    # =====================================================================

    @classmethod
    def normalize_industry(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Resolve canonical industry metadata.

        Supported provider field names include:

            industry
            industry_name
            industryName
            industry_description
            industryDescription
            gics_industry
            gicsIndustry
            sic_industry
            sicIndustry
            naics_industry
            naicsIndustry
            industry_title
            industryTitle

        IMPORTANT:

            sector is deliberately NOT included.
        """

        value = cls._resolve_classification_field(
            data,
            "industry",
            "industry_name",
            "industryName",
            "industry_description",
            "industryDescription",
            "industry_title",
            "industryTitle",
            "gics_industry",
            "gicsIndustry",
            "sic_industry",
            "sicIndustry",
            "naics_industry",
            "naicsIndustry",
        )

        return cls.normalize_text(value)

    # =====================================================================
    # Sub-Industry
    # =====================================================================

    @classmethod
    def normalize_sub_industry(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Resolve canonical sub-industry metadata.
        """

        value = cls._resolve_classification_field(
            data,
            "sub_industry",
            "subindustry",
            "subIndustry",
            "sub_industry_name",
            "subIndustryName",
            "industry_group",
            "industryGroup",
            "industry_group_name",
            "industryGroupName",
            "gics_sub_industry",
            "gicsSubIndustry",
            "sic_sub_industry",
            "sicSubIndustry",
            "naics_sub_industry",
            "naicsSubIndustry",
        )

        return cls.normalize_text(value)

    # =====================================================================
    # Classification
    # =====================================================================

    @classmethod
    def normalize_classification(
        cls,
        data: dict[str, Any],
    ) -> dict[str, str]:
        """
        Normalize all classification dimensions independently.

        Returns only meaningful values.

        IMPORTANT:

            sector != industry
            sector is never promoted to industry.
        """

        if not isinstance(data, dict):
            return {}

        classification: dict[str, str] = {}

        sector = cls.normalize_sector(data)

        if sector:
            classification["sector"] = sector

        industry = cls.normalize_industry(data)

        if industry:
            classification["industry"] = industry

        sub_industry = cls.normalize_sub_industry(data)

        if sub_industry:
            classification["sub_industry"] = sub_industry

        return classification

    # =====================================================================
    # Exchange
    # =====================================================================

    @classmethod
    def normalize_exchange(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Resolve and normalize exchange.
        """

        value = cls._resolve_field(
            data,
            "exchange",
            "exchange_name",
            "exchangeName",
            "exchange_code",
            "exchangeCode",
        )

        return cls.normalize_text(value)

    # =====================================================================
    # Description
    # =====================================================================

    @classmethod
    def normalize_description(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Resolve company description.
        """

        value = cls._resolve_field(
            data,
            "description",
            "business_description",
            "businessDescription",
            "company_description",
            "companyDescription",
            "summary",
        )

        return cls.normalize_text(value)

    # =====================================================================
    # Headquarters
    # =====================================================================

    @classmethod
    def normalize_headquarters(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Resolve headquarters information.
        """

        value = cls._resolve_field(
            data,
            "headquarters",
            "headquarter",
            "hq",
            "headquarters_location",
            "headquartersLocation",
        )

        return cls.normalize_text(value)

    # =====================================================================
    # Legal Name
    # =====================================================================

    @classmethod
    def normalize_legal_name(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Resolve legal company name.
        """

        value = cls._resolve_field(
            data,
            "legal_name",
            "legalName",
            "registered_name",
            "registeredName",
        )

        return cls.normalize_name(value)

    # =====================================================================
    # Main Normalizer
    # =====================================================================

    @classmethod
    def normalize(
        cls,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize raw company/provider data.

        Provider-specific fields are preserved unless they
        conflict with canonical fields.

        Canonical classification is always represented as:

            sector
            industry
            sub_industry

        Missing values are represented by None.

        Existing meaningful provider values are preserved.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "CompanyNormalizer.normalize() requires "
                "a dictionary."
            )

        # Start from a copy so provider-specific metadata is
        # preserved.
        normalized = dict(data)

        # ==============================================================
        # Company Name
        # ==============================================================

        raw_name = cls._resolve_field(
            data,
            "name",
            "company_name",
            "companyName",
            "company",
            "legal_name",
            "legalName",
        )

        name = cls.normalize_name(
            raw_name,
        )

        normalized["name"] = name

        if name:
            normalized["company_name"] = name
            normalized["company"] = name
            normalized["normalized_name"] = (
                cls.normalize_name_for_matching(
                    name,
                )
            )
        else:
            normalized.setdefault(
                "company_name",
                None,
            )

            normalized.setdefault(
                "company",
                None,
            )

            normalized["normalized_name"] = None

        # ==============================================================
        # Ticker
        # ==============================================================

        raw_ticker = cls._resolve_field(
            data,
            "ticker",
            "symbol",
            "stock_symbol",
            "stockSymbol",
            "ticker_symbol",
            "tickerSymbol",
        )

        ticker = cls.normalize_ticker(
            raw_ticker,
        )

        normalized["ticker"] = ticker

        if ticker:
            normalized["symbol"] = ticker

        # ==============================================================
        # Website
        # ==============================================================

        website = cls._resolve_field(
            data,
            "website",
            "web_site",
            "homepage",
            "url",
            "website_url",
            "websiteUrl",
        )

        normalized["website"] = cls.normalize_website(
            website,
        )

        # ==============================================================
        # Country
        # ==============================================================

        country = cls._resolve_field(
            data,
            "country",
            "country_name",
            "countryName",
            "country_code",
            "countryCode",
        )

        normalized["country"] = cls.normalize_country(
            country,
        )

        # ==============================================================
        # Classification
        # ==============================================================

        classification = cls.normalize_classification(
            data,
        )

        # --------------------------------------------------------------
        # IMPORTANT:
        #
        # We only replace canonical fields with a meaningful
        # normalized value.
        #
        # This prevents an incomplete provider response from
        # destroying already-known metadata.
        # --------------------------------------------------------------

        for field in (
            "sector",
            "industry",
            "sub_industry",
        ):
            value = classification.get(field)

            if value:
                normalized[field] = value

            elif field not in normalized:
                normalized[field] = None

            else:
                existing = normalized.get(field)

                if isinstance(existing, str):
                    existing = cls.normalize_text(
                        existing,
                    )

                normalized[field] = existing

        # ==============================================================
        # Common Company Fields
        # ==============================================================

        exchange = cls.normalize_exchange(
            data,
        )

        if exchange:
            normalized["exchange"] = exchange
        else:
            normalized.setdefault(
                "exchange",
                None,
            )

        description = cls.normalize_description(
            data,
        )

        if description:
            normalized["description"] = description
        else:
            normalized.setdefault(
                "description",
                None,
            )

        headquarters = cls.normalize_headquarters(
            data,
        )

        if headquarters:
            normalized["headquarters"] = headquarters
        else:
            normalized.setdefault(
                "headquarters",
                None,
            )

        legal_name = cls.normalize_legal_name(
            data,
        )

        if legal_name:
            normalized["legal_name"] = legal_name
        else:
            normalized.setdefault(
                "legal_name",
                None,
            )

        # ==============================================================
        # Canonical Classification Guarantee
        # ==============================================================

        # Never derive industry from sector.
        #
        # Never derive sub_industry from industry.
        #
        # They remain independent canonical fields.

        normalized.setdefault(
            "sector",
            None,
        )

        normalized.setdefault(
            "industry",
            None,
        )

        normalized.setdefault(
            "sub_industry",
            None,
        )

        return normalized


__all__ = [
    "CompanyNormalizer",
]

