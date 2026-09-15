"""
app/company_catalog/providers/provider_manager.py

Company Provider Manager.

Responsibilities
----------------
- Register company-data providers.
- Search companies across registered providers.
- Retrieve company profiles.
- List companies for synchronization.
- Check provider health.
- Deduplicate provider results.
- Keep provider orchestration outside CompanySearchService.

Architecture
------------

CompanySearchService
        |
        v
CompanyProviderManager
        |
        +------------------+
        |                  |
        v                  v
   YahooProvider      SECProvider
        |
        +-- PolygonProvider
        +-- AlphaVantageProvider
        +-- OpenFIGIProvider
        +-- CrunchbaseProvider


IMPORTANT
---------

This manager belongs to the COMPANY CATALOG layer.

It must NOT be confused with:

    app/financial/providers/provider_manager.py

which contains FinancialProviderManager and handles:

    - prices
    - financial statements
    - market data
    - valuation data
    - analyst estimates
    - dividends
    - historical market data
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from .base import BaseProvider


logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================


class CompanyProviderError(Exception):
    """
    Base exception for company provider failures.
    """


class CompanyProviderNotFoundError(CompanyProviderError):
    """
    Raised when a requested company provider is unavailable.
    """


# ============================================================================
# Company Provider Manager
# ============================================================================


class CompanyProviderManager:
    """
    Central manager for company catalog providers.

    Providers implement:

        BaseProvider
            |
            +-- name
            +-- search_company()
            +-- list_companies()
            +-- get_company_profile()
            +-- health_check()

    The manager exposes application-level operations:

        search()
        list_companies()
        get_company_profile()
        health_check()

    The manager handles:

        - provider selection
        - provider failures
        - async/sync compatibility
        - result normalization
        - result deduplication

    Individual provider implementations remain responsible
    for external API access and provider-specific normalization.
    """

    def __init__(
        self,
        *,
        providers: list[BaseProvider] | None = None,
    ) -> None:
        """
        Initialize the company provider manager.
        """

        self._providers: dict[str, BaseProvider] = {}

        if providers:
            for provider in providers:
                self.register(provider)

    # ========================================================================
    # Provider Registration
    # ========================================================================

    def register(
        self,
        provider: BaseProvider,
    ) -> None:
        """
        Register a company provider.
        """

        if not isinstance(provider, BaseProvider):
            raise TypeError(
                "Provider must inherit from "
                "app.company_catalog.providers.base.BaseProvider."
            )

        provider_name = self._provider_name(provider)

        if not provider_name:
            raise ValueError(
                "Company provider name cannot be empty."
            )

        if provider_name == "base":
            raise ValueError(
                "Concrete company providers must define "
                "their own provider name."
            )

        if provider_name in self._providers:
            logger.warning(
                "Replacing existing company provider | provider=%s",
                provider_name,
            )

        self._providers[provider_name] = provider

        logger.info(
            "Company provider registered | provider=%s",
            provider_name,
        )

    # ========================================================================
    # Provider Lookup
    # ========================================================================

    def get_provider(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Return a registered company provider.
        """

        if not isinstance(name, str):
            raise TypeError(
                "Provider name must be a string."
            )

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise ValueError(
                "Provider name cannot be empty."
            )

        provider = self._providers.get(normalized_name)

        if provider is None:
            raise CompanyProviderNotFoundError(
                f"Company provider '{normalized_name}' "
                f"is not registered. "
                f"Available providers: {self.list_providers()}"
            )

        return provider

    # ========================================================================
    # Provider Existence
    # ========================================================================

    def has_provider(
        self,
        name: str,
    ) -> bool:
        """
        Return True when the provider is registered.
        """

        if not isinstance(name, str):
            return False

        normalized_name = name.strip().lower()

        if not normalized_name:
            return False

        return normalized_name in self._providers

    # ========================================================================
    # Provider Listing
    # ========================================================================

    def list_providers(self) -> list[str]:
        """
        Return registered provider names.
        """

        return sorted(self._providers.keys())

    # ========================================================================
    # Company Search
    # ========================================================================

    async def search(
        self,
        query: str,
        *,
        providers: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search companies across registered providers.

        Individual provider failures are isolated. A failure from
        one provider does not fail the complete search.
        """

        if not isinstance(query, str):
            raise TypeError(
                "Company search query must be a string."
            )

        normalized_query = query.strip()

        if not normalized_query:
            return []

        selected_providers = self._select_providers(providers)

        if not selected_providers:
            logger.warning(
                "Company provider search requested but no providers "
                "are registered | query=%r",
                normalized_query,
            )
            return []

        logger.info(
            "Company provider search started | query=%r | providers=%s",
            normalized_query,
            [
                self._provider_name(provider)
                for provider in selected_providers
            ],
        )

        results: list[dict[str, Any]] = []

        for provider in selected_providers:
            provider_name = self._provider_name(provider)

            try:
                provider_result = provider.search_company(
                    normalized_query
                )

                if inspect.isawaitable(provider_result):
                    provider_result = await provider_result

                if provider_result is None:
                    logger.debug(
                        "Company provider returned no results | "
                        "provider=%s | query=%r",
                        provider_name,
                        normalized_query,
                    )
                    continue

                if not isinstance(provider_result, list):
                    logger.warning(
                        "Company provider returned invalid search result | "
                        "provider=%s | type=%s",
                        provider_name,
                        type(provider_result).__name__,
                    )
                    continue

                provider_count = 0

                for item in provider_result:
                    if not isinstance(item, dict):
                        logger.debug(
                            "Ignoring non-dict company provider result | "
                            "provider=%s | type=%s",
                            provider_name,
                            type(item).__name__,
                        )
                        continue

                    normalized_item = dict(item)

                    normalized_item.setdefault(
                        "source",
                        provider_name,
                    )

                    results.append(normalized_item)
                    provider_count += 1

                logger.info(
                    "Company provider search completed | "
                    "provider=%s | query=%r | results=%d",
                    provider_name,
                    normalized_query,
                    provider_count,
                )

            except Exception:
                logger.exception(
                    "Company provider search failed | "
                    "provider=%s | query=%r",
                    provider_name,
                    normalized_query,
                )

        deduplicated = self._deduplicate_results(results)

        logger.info(
            "Company provider search finished | "
            "query=%r | raw_results=%d | deduplicated_results=%d",
            normalized_query,
            len(results),
            len(deduplicated),
        )

        return deduplicated

    # ========================================================================
    # Company Profile
    # ========================================================================

    async def get_company_profile(
        self,
        symbol: str,
        *,
        provider: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve a company profile.

        If provider is specified, only that provider is used.

        Otherwise providers are tried in registration order until
        one returns a meaningful profile.
        """

        if not isinstance(symbol, str):
            raise TypeError(
                "Company symbol must be a string."
            )

        normalized_symbol = symbol.strip()

        if not normalized_symbol:
            return {}

        if provider is not None:
            selected_provider = self.get_provider(provider)

            try:
                return await self._get_profile(
                    selected_provider,
                    normalized_symbol,
                )
            except Exception:
                logger.exception(
                    "Company profile lookup failed | "
                    "provider=%s | symbol=%s",
                    self._provider_name(selected_provider),
                    normalized_symbol,
                )
                return {}

        for selected_provider in self._providers.values():
            provider_name = self._provider_name(
                selected_provider
            )

            try:
                result = await self._get_profile(
                    selected_provider,
                    normalized_symbol,
                )

                if result:
                    return result

            except Exception:
                logger.exception(
                    "Company profile lookup failed | "
                    "provider=%s | symbol=%s",
                    provider_name,
                    normalized_symbol,
                )

        return {}

    # ========================================================================
    # Bulk Company Listing
    # ========================================================================

    async def list_companies(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        providers: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve companies from registered providers.

        limit is applied per provider because providers may have
        independent pagination systems.
        """

        if not isinstance(limit, int):
            raise TypeError(
                "limit must be an integer."
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        if not isinstance(offset, int):
            raise TypeError(
                "offset must be an integer."
            )

        if offset < 0:
            raise ValueError(
                "offset cannot be negative."
            )

        selected_providers = self._select_providers(providers)

        if not selected_providers:
            logger.warning(
                "Company provider listing requested but "
                "no providers are registered."
            )
            return []

        results: list[dict[str, Any]] = []

        for provider in selected_providers:
            provider_name = self._provider_name(provider)

            try:
                provider_result = provider.list_companies(
                    limit=limit,
                    offset=offset,
                )

                if inspect.isawaitable(provider_result):
                    provider_result = await provider_result

                if provider_result is None:
                    continue

                if not isinstance(provider_result, list):
                    logger.warning(
                        "Company provider returned invalid "
                        "list_companies result | provider=%s | type=%s",
                        provider_name,
                        type(provider_result).__name__,
                    )
                    continue

                for item in provider_result:
                    if not isinstance(item, dict):
                        continue

                    normalized_item = dict(item)

                    normalized_item.setdefault(
                        "source",
                        provider_name,
                    )

                    results.append(normalized_item)

            except Exception:
                logger.exception(
                    "Company provider bulk listing failed | "
                    "provider=%s | limit=%d | offset=%d",
                    provider_name,
                    limit,
                    offset,
                )

        return self._deduplicate_results(results)

    # ========================================================================
    # Health Check
    # ========================================================================

    async def health_check(
        self,
    ) -> dict[str, bool]:
        """
        Check all registered company providers.
        """

        result: dict[str, bool] = {}

        for provider_name, provider in self._providers.items():
            try:
                health_check = getattr(
                    provider,
                    "health_check",
                    None,
                )

                if not callable(health_check):
                    logger.warning(
                        "Company provider has no callable health_check() | "
                        "provider=%s",
                        provider_name,
                    )

                    result[provider_name] = False
                    continue

                health_result = health_check()

                if inspect.isawaitable(health_result):
                    health_result = await health_result

                result[provider_name] = bool(health_result)

            except Exception:
                logger.exception(
                    "Company provider health check failed | "
                    "provider=%s",
                    provider_name,
                )

                result[provider_name] = False

        return result

    # ========================================================================
    # Internal Provider Selection
    # ========================================================================

    def _select_providers(
        self,
        providers: list[str] | None,
    ) -> list[BaseProvider]:
        """
        Resolve requested provider names.

        If providers is None, all registered providers are returned.
        """

        if providers is None:
            return list(self._providers.values())

        selected: list[BaseProvider] = []
        seen: set[str] = set()

        for provider_name in providers:
            if not isinstance(provider_name, str):
                raise TypeError(
                    "Provider names must be strings."
                )

            normalized_name = provider_name.strip().lower()

            if not normalized_name:
                continue

            if normalized_name in seen:
                continue

            selected.append(
                self.get_provider(normalized_name)
            )

            seen.add(normalized_name)

        return selected

    # ========================================================================
    # Internal Profile Execution
    # ========================================================================

    async def _get_profile(
        self,
        provider: BaseProvider,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Safely execute get_company_profile().
        """

        provider_name = self._provider_name(provider)

        result = provider.get_company_profile(symbol)

        if inspect.isawaitable(result):
            result = await result

        if result is None:
            return {}

        if not isinstance(result, dict):
            logger.warning(
                "Company provider returned invalid profile | "
                "provider=%s | symbol=%s | type=%s",
                provider_name,
                symbol,
                type(result).__name__,
            )

            return {}

        normalized_result = dict(result)

        normalized_result.setdefault(
            "source",
            provider_name,
        )

        return normalized_result

    # ========================================================================
    # Deduplication
    # ========================================================================

    @staticmethod
    def _deduplicate_results(
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Remove obvious duplicate provider results.

        Identity priority:

            1. CIK
            2. LEI
            3. FIGI
            4. Ticker + exchange
            5. Name
            6. Deterministic record representation

        More complete records are merged into existing records.
        """

        unique: dict[str, dict[str, Any]] = {}

        for result in results:
            key = CompanyProviderManager._build_result_key(
                result
            )

            if key not in unique:
                unique[key] = dict(result)
                continue

            existing = unique[key]
            merged = dict(existing)

            # Fill missing fields first.
            for field, value in result.items():
                if value is None or value == "":
                    continue

                existing_value = merged.get(field)

                if existing_value is None or existing_value == "":
                    merged[field] = value

            # If incoming record is more complete, prefer it for
            # non-critical provider fields.
            if len(result) > len(existing):
                for field, value in result.items():
                    if field == "source":
                        continue

                    if value is not None and value != "":
                        merged[field] = value

            # Preserve the first known source.
            if not merged.get("source"):
                merged["source"] = result.get("source")

            unique[key] = merged

        return list(unique.values())

    # ========================================================================
    # Result Identity
    # ========================================================================

    @staticmethod
    def _build_result_key(
        result: dict[str, Any],
    ) -> str:
        """
        Build a stable identity key for a provider result.

        Priority:

            CIK
            LEI
            FIGI
            Ticker + exchange
            Company name
            Deterministic record representation
        """

        cik = result.get("cik")

        if cik:
            return (
                "cik:"
                + str(cik).strip().lower()
            )

        lei = result.get("lei")

        if lei:
            return (
                "lei:"
                + str(lei).strip().lower()
            )

        figi = result.get("figi")

        if figi:
            return (
                "figi:"
                + str(figi).strip().lower()
            )

        ticker = (
            result.get("ticker")
            or result.get("symbol")
            or result.get("stock_symbol")
        )

        exchange = result.get("exchange")

        if ticker:
            ticker_value = (
                str(ticker)
                .strip()
                .lower()
            )

            exchange_value = (
                str(exchange or "")
                .strip()
                .lower()
            )

            return (
                f"ticker:{ticker_value}:"
                f"{exchange_value}"
            )

        name = (
            result.get("name")
            or result.get("company_name")
            or result.get("legal_name")
        )

        if name:
            normalized_name = " ".join(
                str(name)
                .strip()
                .lower()
                .split()
            )

            return (
                "name:"
                + normalized_name
            )

        try:
            items = sorted(
                (
                    str(key),
                    repr(value),
                )
                for key, value in result.items()
            )

            return (
                "record:"
                + repr(items)
            )

        except Exception:
            return (
                "record:"
                + repr(result)
            )

    # ========================================================================
    # Provider Name
    # ========================================================================

    @staticmethod
    def _provider_name(
        provider: BaseProvider,
    ) -> str:
        """
        Safely retrieve and normalize provider name.
        """

        name = getattr(
            provider,
            "name",
            None,
        )

        if callable(name):
            try:
                name = name()
            except Exception:
                name = None

        if name is None:
            name = provider.__class__.__name__

        return (
            str(name)
            .strip()
            .lower()
        )


__all__ = [
    "CompanyProviderManager",
    "CompanyProviderError",
    "CompanyProviderNotFoundError",
]