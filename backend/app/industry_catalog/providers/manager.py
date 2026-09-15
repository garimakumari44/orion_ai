"""
app/industry_catalog/providers/manager.py

Industry Provider Manager.

Responsibilities
----------------
- register industry providers
- select providers
- execute provider searches
- aggregate provider results
- handle provider failures
- expose provider health
- manage provider lifecycle

The manager does NOT:
- persist Industry records
- perform research
- run research agents
- own repository/database logic
- contain provider-specific implementation details
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .base import IndustryProvider

logger = logging.getLogger(__name__)


class IndustryProviderManager:
    """
    Coordinates multiple Industry Catalog providers.

    This class is application-level infrastructure.

    It does not:
    - own database sessions
    - persist Industry records
    - perform research
    - execute agents
    - perform LLM analysis
    """

    def __init__(
        self,
        providers: Optional[Iterable[IndustryProvider]] = None,
        *,
        fail_fast: bool = False,
    ) -> None:
        self.fail_fast = fail_fast

        self._providers: Dict[str, IndustryProvider] = {}

        if providers:
            for provider in providers:
                self.register(provider)

    # ==================================================================
    # Provider registration
    # ==================================================================

    def register(
        self,
        provider: IndustryProvider,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register an industry provider.
        """

        if not isinstance(
            provider,
            IndustryProvider,
        ):
            raise TypeError(
                "provider must be an instance of IndustryProvider"
            )

        name = self._clean_string(
            provider.provider_name
        )

        if not name:
            raise ValueError(
                "Industry provider name cannot be empty"
            )

        if (
            name in self._providers
            and not replace
        ):
            raise ValueError(
                f"Industry provider '{name}' "
                "is already registered"
            )

        self._providers[name] = provider

        logger.info(
            "Registered industry provider: %s",
            name,
        )

    # ==================================================================
    # Provider removal
    # ==================================================================

    def unregister(
        self,
        provider_name: str,
    ) -> bool:
        """
        Remove a provider.
        """

        provider = self._providers.pop(
            provider_name,
            None,
        )

        if provider is None:
            return False

        try:
            provider.close()

        except Exception:
            logger.exception(
                "Error closing industry provider '%s'",
                provider_name,
            )

        logger.info(
            "Unregistered industry provider: %s",
            provider_name,
        )

        return True

    # ==================================================================
    # Provider access
    # ==================================================================

    def get_provider(
        self,
        provider_name: str,
    ) -> Optional[IndustryProvider]:
        """
        Return a provider by name.
        """

        return self._providers.get(
            provider_name
        )

    def require_provider(
        self,
        provider_name: str,
    ) -> IndustryProvider:
        """
        Return a provider or raise ValueError.
        """

        provider = self.get_provider(
            provider_name
        )

        if provider is None:
            raise ValueError(
                f"Industry provider '{provider_name}' "
                "is not registered"
            )

        return provider

    def list_providers(
        self,
    ) -> List[IndustryProvider]:
        """
        Return providers ordered by priority.
        """

        return sorted(
            self._providers.values(),
            key=lambda provider: provider.priority,
        )

    def provider_names(
        self,
    ) -> List[str]:
        """
        Return registered provider names.
        """

        return [
            provider.provider_name
            for provider in self.list_providers()
        ]

    # ==================================================================
    # Enabled providers
    # ==================================================================

    def get_enabled_providers(
        self,
    ) -> List[IndustryProvider]:
        """
        Return enabled providers ordered by priority.
        """

        return [
            provider
            for provider in self.list_providers()
            if provider.enabled
        ]

    # ==================================================================
    # Industry search
    # ==================================================================

    def search_industry(
        self,
        query: Optional[str] = None,
        *,
        industry: Optional[str] = None,
        company: Optional[str] = None,
        ticker: Optional[str] = None,
        limit: int = 20,
        providers: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Search selected industry providers.

        Supports both legacy and canonical calling styles.

        Legacy:

            search_industry(
                "semiconductors",
                limit=20,
            )

        Canonical:

            search_industry(
                industry="semiconductors",
                company="NVIDIA",
                ticker="NVDA",
            )

        The explicit industry value takes precedence over query.
        """

        # --------------------------------------------------------------
        # Validate limit
        # --------------------------------------------------------------

        if limit <= 0:
            return []

        # --------------------------------------------------------------
        # Resolve canonical query
        # --------------------------------------------------------------

        resolved_query = (
            self._clean_string(industry)
            or self._clean_string(query)
        )

        if not resolved_query:
            return []

        # --------------------------------------------------------------
        # Resolve providers
        # --------------------------------------------------------------

        selected = self._resolve_provider_selection(
            providers
        )

        results: List[Dict[str, Any]] = []

        # --------------------------------------------------------------
        # Execute providers
        # --------------------------------------------------------------

        for provider in selected:

            if not provider.enabled:
                continue

            try:

                provider_results = (
                    provider.search_industry(
                        resolved_query,
                        limit=limit,
                        company=company,
                        ticker=ticker,
                        **kwargs,
                    )
                )

                if not provider_results:
                    continue

                for result in provider_results:

                    if not isinstance(
                        result,
                        dict,
                    ):
                        logger.warning(
                            "Industry provider '%s' returned "
                            "non-dict search result; skipping",
                            provider.provider_name,
                        )

                        continue

                    normalized = dict(result)

                    normalized.setdefault(
                        "_provider",
                        provider.provider_name,
                    )

                    results.append(
                        normalized
                    )

            except Exception:

                logger.exception(
                    "Industry provider '%s' failed during "
                    "industry search | query=%r | "
                    "company=%r | ticker=%r",
                    provider.provider_name,
                    resolved_query,
                    company,
                    ticker,
                )

                if self.fail_fast:
                    raise

        return self._deduplicate_results(
            results,
            limit=limit,
        )

    # ==================================================================
    # Industry lookup
    # ==================================================================

    def get_industry(
        self,
        industry: str,
        *,
        providers: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve an industry from providers in priority order.
        """

        normalized_industry = self._clean_string(
            industry
        )

        if not normalized_industry:
            return None

        selected = self._resolve_provider_selection(
            providers
        )

        for provider in selected:

            if not provider.enabled:
                continue

            try:

                result = provider.get_industry(
                    normalized_industry,
                    **kwargs,
                )

                if result is None:
                    continue

                if not isinstance(
                    result,
                    dict,
                ):
                    logger.warning(
                        "Industry provider '%s' returned "
                        "invalid lookup result; skipping",
                        provider.provider_name,
                    )

                    continue

                if not result:
                    continue

                normalized = dict(result)

                normalized.setdefault(
                    "_provider",
                    provider.provider_name,
                )

                return normalized

            except Exception:

                logger.exception(
                    "Industry provider '%s' failed during "
                    "industry lookup",
                    provider.provider_name,
                )

                if self.fail_fast:
                    raise

        return None

    # ==================================================================
    # Company classification
    # ==================================================================

    def classify_company(
        self,
        company: Optional[str] = None,
        *,
        ticker: Optional[str] = None,
        providers: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Ask providers to classify a company.

        The first valid non-empty dictionary result wins.
        """

        company = self._clean_string(
            company
        )

        ticker = self._clean_string(
            ticker
        )

        if not company and not ticker:
            return None

        selected = self._resolve_provider_selection(
            providers
        )

        for provider in selected:

            if not provider.enabled:
                continue

            try:

                result = provider.classify_company(
                    company=company,
                    ticker=ticker,
                    **kwargs,
                )

                if result is None:
                    continue

                if not isinstance(
                    result,
                    dict,
                ):
                    logger.warning(
                        "Industry provider '%s' returned invalid "
                        "classification type '%s'; skipping",
                        provider.provider_name,
                        type(result).__name__,
                    )

                    continue

                if not result:
                    continue

                normalized = dict(result)

                normalized.setdefault(
                    "_provider",
                    provider.provider_name,
                )

                return normalized

            except Exception:

                logger.exception(
                    "Industry provider '%s' failed during "
                    "company classification",
                    provider.provider_name,
                )

                if self.fail_fast:
                    raise

        return None

    # ==================================================================
    # Taxonomy
    # ==================================================================

    def get_taxonomy(
        self,
        *,
        taxonomy: Optional[str] = None,
        providers: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve taxonomy data from selected providers.
        """

        selected = self._resolve_provider_selection(
            providers
        )

        results: List[Dict[str, Any]] = []

        for provider in selected:

            if not provider.enabled:
                continue

            try:

                provider_results = provider.get_taxonomy(
                    taxonomy=taxonomy,
                    **kwargs,
                )

                if not provider_results:
                    continue

                for result in provider_results:

                    if not isinstance(
                        result,
                        dict,
                    ):
                        logger.warning(
                            "Industry provider '%s' returned "
                            "invalid taxonomy result; skipping",
                            provider.provider_name,
                        )

                        continue

                    normalized = dict(result)

                    normalized.setdefault(
                        "_provider",
                        provider.provider_name,
                    )

                    results.append(
                        normalized
                    )

            except Exception:

                logger.exception(
                    "Industry provider '%s' failed during "
                    "taxonomy retrieval",
                    provider.provider_name,
                )

                if self.fail_fast:
                    raise

        return self._deduplicate_results(
            results
        )

    # ==================================================================
    # Health
    # ==================================================================

    def health_check(
        self,
    ) -> Dict[str, bool]:
        """
        Check health of all registered providers.
        """

        health: Dict[str, bool] = {}

        for provider in self.list_providers():

            try:

                health[
                    provider.provider_name
                ] = bool(
                    provider.health_check()
                )

            except Exception:

                logger.exception(
                    "Health check failed for industry provider '%s'",
                    provider.provider_name,
                )

                health[
                    provider.provider_name
                ] = False

        return health

    # ==================================================================
    # Provider selection
    # ==================================================================

    def _resolve_provider_selection(
        self,
        providers: Optional[Sequence[str]],
    ) -> List[IndustryProvider]:
        """
        Resolve requested providers.
        """

        if providers is None:
            return self.get_enabled_providers()

        selected: List[IndustryProvider] = []

        for name in providers:

            normalized_name = self._clean_string(
                name
            )

            if not normalized_name:
                continue

            provider = self._providers.get(
                normalized_name
            )

            if provider is None:

                logger.warning(
                    "Requested industry provider '%s' "
                    "is not registered",
                    normalized_name,
                )

                continue

            if not provider.enabled:
                continue

            selected.append(
                provider
            )

        return selected

    # ==================================================================
    # Result deduplication
    # ==================================================================

    @staticmethod
    def _deduplicate_results(
        results: List[Dict[str, Any]],
        *,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate provider results.
        """

        seen: set[str] = set()

        deduplicated: List[Dict[str, Any]] = []

        for result in results:

            key = (
                IndustryProviderManager
                ._result_identity(result)
            )

            if key in seen:
                continue

            seen.add(key)

            deduplicated.append(
                result
            )

            if (
                limit is not None
                and len(deduplicated) >= limit
            ):
                break

        return deduplicated

    @staticmethod
    def _result_identity(
        result: Dict[str, Any],
    ) -> str:
        """
        Build a stable identity key.
        """

        industry_id = result.get(
            "industry_id"
        )

        if industry_id:
            return (
                "id:"
                f"{str(industry_id).strip().lower()}"
            )

        code = result.get(
            "code"
        )

        if code:
            return (
                "code:"
                f"{str(code).strip().lower()}"
            )

        industry = result.get(
            "industry"
        )

        sub_industry = result.get(
            "sub_industry"
        )

        if industry and sub_industry:

            return (
                "industry_sub:"
                f"{str(industry).strip().lower()}|"
                f"{str(sub_industry).strip().lower()}"
            )

        if industry:

            return (
                "industry:"
                f"{str(industry).strip().lower()}"
            )

        try:

            stable_items = sorted(
                (
                    str(key),
                    repr(value),
                )
                for key, value in result.items()
            )

            return f"raw:{repr(stable_items)}"

        except Exception:

            return f"raw:{repr(result)}"

    # ==================================================================
    # Utility
    # ==================================================================

    @staticmethod
    def _clean_string(
        value: Any,
    ) -> Optional[str]:
        """
        Normalize arbitrary value into a string.
        """

        if value is None:
            return None

        value = str(value).strip()

        return value or None

    # ==================================================================
    # Shutdown
    # ==================================================================

    def close(self) -> None:
        """
        Close all registered providers.
        """

        for provider in self._providers.values():

            try:

                provider.close()

            except Exception:

                logger.exception(
                    "Error closing industry provider '%s'",
                    provider.provider_name,
                )

    # ==================================================================
    # Context manager
    # ==================================================================

    def __enter__(
        self,
    ) -> "IndustryProviderManager":

        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:

        self.close()

    # ==================================================================
    # Representation
    # ==================================================================

    def __repr__(
        self,
    ) -> str:

        providers = ", ".join(
            self.provider_names()
        )

        return (
            f"{self.__class__.__name__}("
            f"providers=[{providers}]"
            f")"
        )


# ======================================================================
# Backward-compatible aliases
# ======================================================================

ProviderManager = IndustryProviderManager

IndustryCatalogProviderManager = IndustryProviderManager