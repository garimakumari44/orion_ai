"""
app/services/industry_research_service.py

Industry Research Service.

Application-level orchestration service for industry research.

Canonical architecture:

    Application Composition Root
            |
            v
    IndustryResearchService
            |
            +--> IndustryCatalogManager
            |
            +--> IndustryProviderManager
            |
            v
    normalized industry research data
            |
            v
        IndustryAgent
            |
            +--> deterministic analyzers
            +--> LLM analysis

IMPORTANT:

IndustryResearchService is application-level infrastructure.

It MUST NOT:

- own an AsyncSession
- construct a CompanyRepository
- construct providers
- construct AgentServices
- construct AgentContext
- execute agents
- own ExecutionEngine
- perform LLM analysis
- implement provider-specific API logic
- retain request-scoped database state
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from app.industry_catalog import IndustryCatalogManager
from app.repositories.company_repository import CompanyRepository


logger = logging.getLogger(__name__)


class IndustryResearchService:
    """
    Application-level service for industry research.

    This service is application-scoped.

    Request-scoped CompanyRepository instances must be supplied
    per research operation.

    Shared industry infrastructure is injected by the
    application composition root.
    """

    def __init__(
        self,
        industry_provider_manager: Any | None = None,
        industry_catalog: IndustryCatalogManager | None = None,
    ) -> None:

        if industry_catalog is None:
            raise ValueError(
                "IndustryCatalogManager is required. "
                "It must be created by the application "
                "composition root and injected into "
                "IndustryResearchService."
            )

        self.industry_provider_manager = (
            industry_provider_manager
        )

        self.industry_catalog = industry_catalog

    # =====================================================================
    # Public API
    # =====================================================================

    async def research(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        company_id: int | None = None,
        research_id: int | None = None,
        metadata: dict[str, Any] | None = None,
        context: Any | None = None,
        company_repository: CompanyRepository | None = None,
    ) -> dict[str, Any]:

        metadata = dict(
            metadata or {}
        )

        # --------------------------------------------------------------
        # 1. Context identity
        # --------------------------------------------------------------

        context_identity = (
            self._extract_context_identity(
                context
            )
        )

        if company_id is None:
            company_id = context_identity[
                "company_id"
            ]

        if research_id is None:
            research_id = context_identity[
                "research_id"
            ]

        if company is None:
            company = context_identity[
                "company"
            ]

        if ticker is None:
            ticker = context_identity[
                "ticker"
            ]

        if industry is None:
            industry = context_identity[
                "industry"
            ]

        # --------------------------------------------------------------
        # 2. Metadata fallback
        # --------------------------------------------------------------

        if industry is None:
            industry = self._clean_string(
                metadata.get("industry")
            )

        # --------------------------------------------------------------
        # 3. Repository
        # --------------------------------------------------------------

        repository = (
            self._resolve_company_repository(
                context=context,
                company_repository=company_repository,
            )
        )

        # --------------------------------------------------------------
        # 4. Canonical company
        # --------------------------------------------------------------

        company_record: Any | None = None

        if company_id is not None:

            if repository is None:
                raise RuntimeError(
                    "IndustryResearchService requires a "
                    "request-scoped CompanyRepository when "
                    "company_id is provided."
                )

            company_record = await self._get_company(
                company_id=company_id,
                repository=repository,
            )

            if company_record is None:
                raise ValueError(
                    f"Company with id={company_id} "
                    "was not found."
                )

        # --------------------------------------------------------------
        # 5. Company identity
        # --------------------------------------------------------------

        resolved_company = (
            self._resolve_company_name(
                company_record=company_record,
                fallback_company=company,
            )
        )

        resolved_ticker = (
            self._resolve_ticker(
                company_record=company_record,
                fallback_ticker=ticker,
            )
        )

        # --------------------------------------------------------------
        # 6. Canonical industry
        # --------------------------------------------------------------

        industry_result = (
            await self._resolve_industry_metadata(
                company_record=company_record,
                company=resolved_company,
                ticker=resolved_ticker,
                industry=industry,
                company_id=company_id,
            )
        )

        resolved_industry = (
            self._extract_industry_name(
                industry_result
            )
        )

        if not resolved_industry:
            raise ValueError(
                "Industry research requires a canonical "
                "industry. No industry was found."
            )

        # --------------------------------------------------------------
        # 7. Canonical metadata
        # --------------------------------------------------------------

        canonical_metadata = (
            self._industry_result_to_metadata(
                industry_result
            )
        )

        canonical_metadata.setdefault(
            "company_id",
            company_id,
        )

        canonical_metadata.setdefault(
            "company",
            resolved_company,
        )

        canonical_metadata.setdefault(
            "ticker",
            resolved_ticker,
        )

        canonical_metadata.setdefault(
            "industry",
            resolved_industry,
        )

        logger.info(
            "IndustryResearchService starting | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r",
            research_id,
            company_id,
            resolved_company,
            resolved_ticker,
            resolved_industry,
        )

        # --------------------------------------------------------------
        # 8. Provider research
        # --------------------------------------------------------------

        provider_results = (
            await self._search_providers(
                company=resolved_company,
                ticker=resolved_ticker,
                industry=resolved_industry,
            )
        )

        # --------------------------------------------------------------
        # 9. Normalize
        # --------------------------------------------------------------

        normalized_results = (
            self._normalize_results(
                provider_results=provider_results,
                company=resolved_company,
                ticker=resolved_ticker,
                industry=resolved_industry,
                industry_metadata=canonical_metadata,
            )
        )

        # --------------------------------------------------------------
        # 10. Stable response
        # --------------------------------------------------------------

        result = {
            "research_id": research_id,
            "company_id": company_id,
            "company": resolved_company,
            "ticker": resolved_ticker,
            "industry": resolved_industry,
            "industry_name": resolved_industry,
            "industry_metadata": canonical_metadata,
            "industry_source": canonical_metadata.get(
                "source"
            ),
            "industry_confidence": canonical_metadata.get(
                "confidence"
            ),
            "data": normalized_results,
            "providers": provider_results,
            "metadata": {
                **metadata,
                "company_id": company_id,
                "company": resolved_company,
                "ticker": resolved_ticker,
                "industry": resolved_industry,
                "industry_metadata": canonical_metadata,
            },
        }

        logger.info(
            "IndustryResearchService completed | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r | "
            "provider_count=%d",
            research_id,
            company_id,
            resolved_company,
            resolved_ticker,
            resolved_industry,
            len(provider_results),
        )

        return result

    # =====================================================================
    # Explicit Industry Research
    # =====================================================================

    async def research_industry(
        self,
        *,
        industry: str,
        company: str | None = None,
        ticker: str | None = None,
        company_id: int | None = None,
        research_id: int | None = None,
        metadata: dict[str, Any] | None = None,
        context: Any | None = None,
        company_repository: CompanyRepository | None = None,
    ) -> dict[str, Any]:

        return await self.research(
            company=company,
            ticker=ticker,
            industry=industry,
            company_id=company_id,
            research_id=research_id,
            metadata=metadata,
            context=context,
            company_repository=company_repository,
        )

    # =====================================================================
    # Get Industry
    # =====================================================================

    async def get_industry(
        self,
        *,
        company_id: int | None = None,
        company: str | None = None,
        industry: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: Any | None = None,
        company_repository: CompanyRepository | None = None,
    ) -> dict[str, Any]:

        metadata = dict(
            metadata or {}
        )

        context_identity = (
            self._extract_context_identity(
                context
            )
        )

        if company_id is None:
            company_id = context_identity[
                "company_id"
            ]

        if company is None:
            company = context_identity[
                "company"
            ]

        if industry is None:
            industry = context_identity[
                "industry"
            ]

        if industry is None:
            industry = self._clean_string(
                metadata.get("industry")
            )

        repository = (
            self._resolve_company_repository(
                context=context,
                company_repository=company_repository,
            )
        )

        company_record: Any | None = None

        if company_id is not None:

            if repository is None:
                raise RuntimeError(
                    "IndustryResearchService requires a "
                    "request-scoped CompanyRepository when "
                    "company_id is provided."
                )

            company_record = await self._get_company(
                company_id=company_id,
                repository=repository,
            )

            if company_record is None:
                raise ValueError(
                    f"Company with id={company_id} "
                    "was not found."
                )

        resolved_company = (
            self._resolve_company_name(
                company_record=company_record,
                fallback_company=company,
            )
        )

        resolved_ticker = (
            self._resolve_ticker(
                company_record=company_record,
                fallback_ticker=None,
            )
        )

        industry_result = (
            await self._resolve_industry_metadata(
                company_record=company_record,
                company=resolved_company,
                ticker=resolved_ticker,
                industry=industry,
                company_id=company_id,
            )
        )

        resolved_industry = (
            self._extract_industry_name(
                industry_result
            )
        )

        if not resolved_industry:
            raise ValueError(
                "No canonical industry could be resolved."
            )

        canonical_metadata = (
            self._industry_result_to_metadata(
                industry_result
            )
        )

        canonical_metadata.setdefault(
            "company_id",
            company_id,
        )

        canonical_metadata.setdefault(
            "company",
            resolved_company,
        )

        canonical_metadata.setdefault(
            "ticker",
            resolved_ticker,
        )

        canonical_metadata.setdefault(
            "industry",
            resolved_industry,
        )

        return {
            "company_id": company_id,
            "company": resolved_company,
            "ticker": resolved_ticker,
            "industry": resolved_industry,
            "industry_name": resolved_industry,
            "sub_industry": canonical_metadata.get(
                "sub_industry"
            ),
            "sector": canonical_metadata.get(
                "sector"
            ),
            "confidence": canonical_metadata.get(
                "confidence"
            ),
            "source": canonical_metadata.get(
                "source"
            ),
            "metadata": canonical_metadata,
        }

    # =====================================================================
    # Canonical Industry Resolution
    # =====================================================================

    async def _resolve_industry_metadata(
        self,
        *,
        company_record: Any | None,
        company: str | None,
        ticker: str | None,
        industry: str | None,
        company_id: int | None,
    ) -> Any:

        resolved_company = (
            self._resolve_company_name(
                company_record=company_record,
                fallback_company=company,
            )
        )

        resolved_ticker = (
            self._resolve_ticker(
                company_record=company_record,
                fallback_ticker=ticker,
            )
        )

        resolved_industry: str | None = None

        # --------------------------------------------------------------
        # Company.industry
        # --------------------------------------------------------------

        if company_record is not None:

            resolved_industry = (
                self._clean_string(
                    getattr(
                        company_record,
                        "industry",
                        None,
                    )
                )
            )

            # ----------------------------------------------------------
            # Company.sub_industry fallback
            # ----------------------------------------------------------

            if resolved_industry is None:
                resolved_industry = (
                    self._clean_string(
                        getattr(
                            company_record,
                            "sub_industry",
                            None,
                        )
                    )
                )

        # --------------------------------------------------------------
        # Explicit/context industry
        # --------------------------------------------------------------

        if resolved_industry is None:
            resolved_industry = (
                self._clean_string(
                    industry
                )
            )

        if not resolved_industry:
            raise ValueError(
                "No industry is available for canonical "
                "industry resolution."
            )

        # --------------------------------------------------------------
        # Catalog
        # --------------------------------------------------------------

        result = self.industry_catalog.resolve(
            company_record=company_record,
            company=resolved_company,
            ticker=resolved_ticker,
            industry=resolved_industry,
            company_id=company_id,
        )

        if inspect.isawaitable(result):
            result = await result

        if result is None:
            raise ValueError(
                "IndustryCatalogManager.resolve() "
                "returned None."
            )

        return result

    # =====================================================================
    # Company Identity
    # =====================================================================

    @staticmethod
    def _resolve_company_name(
        *,
        company_record: Any | None,
        fallback_company: str | None,
    ) -> str | None:

        if company_record is not None:

            company_name = (
                IndustryResearchService._clean_string(
                    getattr(
                        company_record,
                        "name",
                        None,
                    )
                )
            )

            if company_name:
                return company_name

        return (
            IndustryResearchService._clean_string(
                fallback_company
            )
        )

    @staticmethod
    def _resolve_ticker(
        *,
        company_record: Any | None,
        fallback_ticker: str | None,
    ) -> str | None:

        if company_record is not None:

            company_ticker = (
                IndustryResearchService._normalize_ticker(
                    getattr(
                        company_record,
                        "ticker",
                        None,
                    )
                )
            )

            if company_ticker:
                return company_ticker

        return (
            IndustryResearchService._normalize_ticker(
                fallback_ticker
            )
        )

    # =====================================================================
    # Industry Result
    # =====================================================================

    @staticmethod
    def _extract_industry_name(
        industry_result: Any,
    ) -> str | None:

        if industry_result is None:
            return None

        if isinstance(
            industry_result,
            dict,
        ):

            for key in (
                "industry",
                "industry_name",
                "name",
            ):

                value = (
                    IndustryResearchService._clean_string(
                        industry_result.get(key)
                    )
                )

                if value:
                    return value

            return None

        for field in (
            "industry",
            "industry_name",
            "name",
        ):

            value = (
                IndustryResearchService._clean_string(
                    getattr(
                        industry_result,
                        field,
                        None,
                    )
                )
            )

            if value:
                return value

        return None

    # =====================================================================
    # Industry Metadata
    # =====================================================================

    @staticmethod
    def _industry_result_to_metadata(
        industry_result: Any,
    ) -> dict[str, Any]:

        if industry_result is None:
            return {}

        if isinstance(
            industry_result,
            dict,
        ):

            return {
                key: value
                for key, value in industry_result.items()
                if value is not None
            }

        metadata: dict[str, Any] = {}

        known_fields = (
            "id",
            "name",
            "slug",
            "industry",
            "industry_name",
            "sub_industry",
            "sector",
            "confidence",
            "source",
            "sic",
            "sic_code",
            "naics",
            "naics_code",
            "gics",
            "gics_code",
            "classification",
            "classification_code",
            "parent_id",
            "parent_industry_id",
            "description",
            "external_id",
            "provider",
            "provider_id",
        )

        for field in known_fields:

            if not hasattr(
                industry_result,
                field,
            ):
                continue

            value = getattr(
                industry_result,
                field,
            )

            if value is not None:
                metadata[field] = value

        return metadata

    # =====================================================================
    # Repository
    # =====================================================================

    @staticmethod
    def _resolve_company_repository(
        *,
        context: Any | None,
        company_repository: CompanyRepository | None,
    ) -> CompanyRepository | None:

        if company_repository is not None:
            return company_repository

        if context is not None:

            context_repository = getattr(
                context,
                "company_repository",
                None,
            )

            if context_repository is not None:
                return context_repository

        return None

    # =====================================================================
    # Context Identity
    # =====================================================================

    @staticmethod
    def _extract_context_identity(
        context: Any | None,
    ) -> dict[str, Any]:

        if context is None:

            return {
                "research_id": None,
                "company_id": None,
                "company": None,
                "ticker": None,
                "industry": None,
            }

        return {
            "research_id": getattr(
                context,
                "research_id",
                None,
            ),
            "company_id": getattr(
                context,
                "company_id",
                None,
            ),
            "company": IndustryResearchService._clean_string(
                getattr(
                    context,
                    "company",
                    None,
                )
            ),
            "ticker": IndustryResearchService._normalize_ticker(
                getattr(
                    context,
                    "ticker",
                    None,
                )
            ),
            "industry": IndustryResearchService._clean_string(
                getattr(
                    context,
                    "industry",
                    None,
                )
            ),
        }

    # =====================================================================
    # Company Retrieval
    # =====================================================================

    @staticmethod
    async def _get_company(
        *,
        company_id: int,
        repository: CompanyRepository,
    ) -> Any | None:

        get_by_id = getattr(
            repository,
            "get_by_id",
            None,
        )

        if not callable(
            get_by_id
        ):
            raise AttributeError(
                "CompanyRepository must provide get_by_id()."
            )

        result = get_by_id(
            company_id
        )

        if inspect.isawaitable(result):
            result = await result

        return result

    # =====================================================================
    # Provider Orchestration
    # =====================================================================

    async def _search_providers(
        self,
        *,
        company: str | None,
        ticker: str | None,
        industry: str,
    ) -> list[dict[str, Any]]:

        manager = (
            self.industry_provider_manager
        )

        if manager is None:

            logger.warning(
                "IndustryResearchService has no "
                "IndustryProviderManager configured."
            )

            return []

        search_industry = getattr(
            manager,
            "search_industry",
            None,
        )

        if not callable(
            search_industry
        ):
            raise AttributeError(
                "IndustryProviderManager must provide "
                "search_industry()."
            )

        try:

            result = search_industry(
                industry=industry,
                company=company,
                ticker=ticker,
            )

            if inspect.isawaitable(result):
                result = await result

        except Exception:

            logger.exception(
                "IndustryProviderManager.search_industry() "
                "failed | industry=%r | company=%r | ticker=%r",
                industry,
                company,
                ticker,
            )

            return []

        return (
            self._normalize_provider_items(
                result
            )
        )

    # =====================================================================
    # Provider Normalization
    # =====================================================================

    @staticmethod
    def _normalize_provider_items(
        value: Any,
    ) -> list[dict[str, Any]]:

        items = (
            IndustryResearchService._ensure_list(
                value
            )
        )

        normalized: list[dict[str, Any]] = []

        for item in items:

            if isinstance(
                item,
                dict,
            ):
                normalized.append(
                    dict(item)
                )
            else:
                normalized.append(
                    {
                        "data": item
                    }
                )

        return normalized

    # =====================================================================
    # Result Normalization
    # =====================================================================

    def _normalize_results(
        self,
        *,
        provider_results: list[dict[str, Any]],
        company: str | None,
        ticker: str | None,
        industry: str,
        industry_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        porter: dict[str, Any] = {}
        market: dict[str, Any] = {}
        market_size: list[Any] = []

        competitors: list[Any] = []
        supply_chain: dict[str, Any] = {}
        trends: list[Any] = []

        companies: list[Any] = []
        statistics: list[Any] = []
        reports: list[Any] = []

        raw: list[Any] = []

        for result in provider_results:

            if not isinstance(
                result,
                dict,
            ):
                raw.append(result)
                continue

            raw.append(
                dict(result)
            )

            # ----------------------------------------------------------
            # Porter
            # ----------------------------------------------------------

            porter_value = self._first_value(
                result,
                "porter",
                "porter_analysis",
                "five_forces",
                "competitive_forces",
            )

            if porter_value is not None:

                if isinstance(
                    porter_value,
                    dict,
                ):
                    porter.update(
                        porter_value
                    )
                else:
                    porter.setdefault(
                        "data",
                        [],
                    )

                    self._extend_value(
                        porter["data"],
                        porter_value,
                    )

            # ----------------------------------------------------------
            # Market
            # ----------------------------------------------------------

            market_value = self._first_value(
                result,
                "market",
                "market_data",
                "market_analysis",
                "market_size",
                "marketSize",
            )

            if market_value is not None:

                if isinstance(
                    market_value,
                    dict,
                ):
                    market.update(
                        market_value
                    )
                else:
                    market.setdefault(
                        "values",
                        [],
                    )

                    self._extend_value(
                        market["values"],
                        market_value,
                    )

            # ----------------------------------------------------------
            # Market size
            # ----------------------------------------------------------

            explicit_market_size = self._first_value(
                result,
                "market_size",
                "marketSize",
            )

            if explicit_market_size is not None:

                self._extend_value(
                    market_size,
                    explicit_market_size,
                )

                if isinstance(
                    explicit_market_size,
                    dict,
                ):
                    market.update(
                        explicit_market_size
                    )

            # ----------------------------------------------------------
            # Competitors
            # ----------------------------------------------------------

            competitor_value = self._first_value(
                result,
                "competitors",
                "competitor",
                "competitive_landscape",
                "competitive_landscape_data",
            )

            self._extend_value(
                competitors,
                competitor_value,
            )

            # ----------------------------------------------------------
            # Supply chain
            # ----------------------------------------------------------

            supply_chain_value = self._first_value(
                result,
                "supply_chain",
                "supply_chain_analysis",
                "supply_chain_data",
                "value_chain",
            )

            if supply_chain_value is not None:

                if isinstance(
                    supply_chain_value,
                    dict,
                ):
                    supply_chain.update(
                        supply_chain_value
                    )
                else:
                    supply_chain.setdefault(
                        "data",
                        [],
                    )

                    self._extend_value(
                        supply_chain["data"],
                        supply_chain_value,
                    )

            # ----------------------------------------------------------
            # Trends
            # ----------------------------------------------------------

            trend_value = self._first_value(
                result,
                "trends",
                "industry_trends",
                "trend",
                "trend_analysis",
            )

            self._extend_value(
                trends,
                trend_value,
            )

            # ----------------------------------------------------------
            # Companies
            # ----------------------------------------------------------

            company_value = self._first_value(
                result,
                "companies",
                "company",
                "company_data",
                "industry_companies",
            )

            self._extend_value(
                companies,
                company_value,
            )

            # ----------------------------------------------------------
            # Statistics
            # ----------------------------------------------------------

            statistics_value = self._first_value(
                result,
                "statistics",
                "stats",
                "metrics",
                "industry_statistics",
            )

            self._extend_value(
                statistics,
                statistics_value,
            )

            # ----------------------------------------------------------
            # Reports
            # ----------------------------------------------------------

            reports_value = self._first_value(
                result,
                "reports",
                "sources",
                "citations",
                "references",
                "research_reports",
            )

            self._extend_value(
                reports,
                reports_value,
            )

        return {
            "company": company,
            "ticker": ticker,
            "industry": industry,
            "industry_metadata": dict(
                industry_metadata or {}
            ),
            "porter": porter,
            "market": market,
            "market_size": market_size,
            "competitors": competitors,
            "supply_chain": supply_chain,
            "trends": trends,
            "companies": companies,
            "statistics": statistics,
            "reports": reports,
            "raw": raw,
        }

    # =====================================================================
    # Utilities
    # =====================================================================

    @staticmethod
    def _ensure_list(
        value: Any,
    ) -> list[Any]:

        if value is None:
            return []

        if isinstance(
            value,
            list,
        ):
            return value

        if isinstance(
            value,
            tuple,
        ):
            return list(value)

        if isinstance(
            value,
            dict,
        ):
            return [value]

        return [value]

    @staticmethod
    def _first_value(
        data: dict[str, Any],
        *keys: str,
    ) -> Any:

        for key in keys:

            value = data.get(key)

            if value is None:
                continue

            if (
                isinstance(value, str)
                and not value.strip()
            ):
                continue

            return value

        return None

    @staticmethod
    def _extend_value(
        target: list[Any],
        value: Any,
    ) -> None:

        if value is None:
            return

        if isinstance(
            value,
            list,
        ):
            target.extend(value)
            return

        if isinstance(
            value,
            tuple,
        ):
            target.extend(value)
            return

        target.append(value)

    @staticmethod
    def _clean_string(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        value = str(value).strip()

        return value or None

    @staticmethod
    def _normalize_ticker(
        value: Any,
    ) -> str | None:

        value = (
            IndustryResearchService._clean_string(
                value
            )
        )

        if not value:
            return None

        return value.upper()