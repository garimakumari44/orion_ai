
"""
app/services/company_research_service.py

Company Research Service.

Responsible for obtaining and enriching company information
before it reaches CompanyAgent's deterministic analyzer and LLM.

Architecture:

    CompanyAgent
          |
          v
    CompanyResearchService
          |
          +---- CompanyRepository       (per research call)
          |
          +---- CompanyProviderManager   (shared)
          |
          +---- CompanyProcessingPipeline (shared)
          |
          v
    Enriched Company Data

IMPORTANT ARCHITECTURAL RULES

1. CompanyResearchService is application-scoped / singleton-safe.

2. CompanyRepository MUST NOT be stored on this service because
   CompanyRepository is bound to a request-scoped AsyncSession.

3. CompanyRepository is supplied for every research call:

       await service.research(
           company_data,
           repository=company_repository,
       )

4. Canonical company identity comes from the research/database
   context and MUST NOT be overwritten by external providers.

5. External providers are enrichment sources only.

6. Provider failures must not destroy valid database/research
   identity.

7. Industry precedence is:

       Company.industry
           |
           v
       Company.sub_industry
           |
           v
       Research.industry

   Company.sector is NOT used as industry.

8. Company research does NOT require a ticker.

   Company identity for external provider discovery is based
   primarily on:

       company_id
       company_name
       CIK
       LEI

   Ticker is retained as metadata for downstream financial
   research but is NOT used as the primary company-provider
   search query.

9. This service does NOT:

   - perform LLM analysis
   - perform investment analysis
   - generate research thesis
   - execute agents
   - own database sessions
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from app.company_catalog.processing.pipeline import (
    CompanyProcessingPipeline,
)
from app.company_catalog.providers.provider_manager import (
    CompanyProviderManager,
)
from app.repositories.company_repository import (
    CompanyRepository,
)

logger = logging.getLogger(__name__)


class CompanyResearchService:
    """
    Retrieves and enriches company information.

    Shared dependencies
    -------------------
    - CompanyProviderManager
    - CompanyProcessingPipeline

    Per-call dependency
    -------------------
    - CompanyRepository

    CompanyAgent should not discover company information directly.

    Instead:

        CompanyAgent
            |
            v
        CompanyResearchService
            |
            +---- Database
            |
            +---- External Providers
            |
            v
        Canonical + Enriched Company Data

    The returned dictionary is provider-agnostic.
    """

    # =========================================================
    # Canonical identity fields
    # =========================================================

    # These fields are protected from external provider overwrite.
    #
    # IMPORTANT:
    #
    # ticker remains canonical when present in the database,
    # but ticker is NOT required for company research.
    #
    # sector is intentionally NOT treated as canonical industry.
    CANONICAL_IDENTITY_FIELDS = {
        "company_id",
        "research_id",
        "company_name",
        "company",
        "name",
        "ticker",
        "symbol",
        "stock_symbol",
        "industry",
    }

    # Provider data is enrichment only.
    PROVIDER_ENRICHMENT_FIELDS = {
        "legal_name",
        "description",
        "website",
        "headquarters",
        "founded_year",
        "employees",
        "country",
        "exchange",
        "market_cap",
        "currency",
        "cik",
        "lei",
        "products",
        "executives",
        "shareholders",
        "operating_regions",
        "business_segments",
        "sources",
        "source",
        "confidence",
        "sub_industry",
    }

    # =========================================================
    # Construction
    # =========================================================

    def __init__(
        self,
        provider_manager: CompanyProviderManager,
        pipeline: CompanyProcessingPipeline,
    ) -> None:
        """
        Initialize the singleton-safe company research service.

        CompanyRepository intentionally does not belong here because
        it requires a request-scoped AsyncSession.
        """

        if provider_manager is None:
            raise ValueError(
                "CompanyProviderManager is required."
            )

        if pipeline is None:
            raise ValueError(
                "CompanyProcessingPipeline is required."
            )

        self.provider_manager = provider_manager
        self.pipeline = pipeline

    # =========================================================
    # Public API
    # =========================================================

    async def research(
        self,
        company_data: dict[str, Any],
        *,
        repository: CompanyRepository,
    ) -> dict[str, Any]:
        """
        Research and enrich a company.

        Example input:

            {
                "research_id": 23,
                "company_id": 10,
                "company": "NVIDIA",
                "company_name": "NVIDIA",
                "ticker": "NVDA",
                "industry": "Semiconductors",
                "query": "...",
                "metadata": {...}
            }

        Ticker is optional for company research.

        External company providers are queried primarily using
        the canonical company name.

        Returns provider-agnostic enriched company data.

        Canonical identity from the research/database context is
        always preserved.
        """

        if not isinstance(company_data, dict):
            raise TypeError(
                "company_data must be a dictionary."
            )

        if repository is None:
            raise ValueError(
                "CompanyResearchService.research() requires "
                "a CompanyRepository for each research call."
            )

        logger.info(
            "CompanyResearchService started | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r",
            company_data.get("research_id"),
            company_data.get("company_id"),
            company_data.get("company")
            or company_data.get("company_name"),
            company_data.get("ticker"),
        )

        # =====================================================
        # 1. Extract research seed
        # =====================================================

        research_id = company_data.get(
            "research_id"
        )

        requested_company_id = company_data.get(
            "company_id"
        )

        requested_company_name = (
            company_data.get("company_name")
            or company_data.get("company")
            or company_data.get("name")
        )

        requested_ticker = (
            company_data.get("ticker")
            or company_data.get("symbol")
            or company_data.get("stock_symbol")
        )

        # IMPORTANT:
        #
        # Do NOT use sector here.
        #
        # ResearchService should already have resolved the canonical
        # industry before invoking this service.

        # =====================================================
        # 2. Validate initial identity
        # =====================================================

        # Ticker is intentionally NOT required.
        #
        # Company research can operate using:
        #
        #   company_id
        #       OR
        #   company name
        #
        if not (
            requested_company_id is not None
            or requested_company_name
        ):
            raise ValueError(
                "CompanyResearchService requires at least "
                "company_id or company name."
            )

        # =====================================================
        # 3. Start with research seed
        # =====================================================

        enriched: dict[str, Any] = dict(company_data)

        # =====================================================
        # 4. Resolve canonical company from database
        # =====================================================

        company_record: Any | None = None

        if requested_company_id is not None:
            logger.info(
                "CompanyResearchService → DATABASE | "
                "research_id=%r | "
                "company_id=%r",
                research_id,
                requested_company_id,
            )

            try:
                company_record = await repository.get_by_id(
                    int(requested_company_id)
                )

            except (TypeError, ValueError):
                logger.exception(
                    "Invalid company_id | "
                    "research_id=%r | "
                    "company_id=%r",
                    research_id,
                    requested_company_id,
                )
                raise

            except Exception:
                logger.exception(
                    "Company database lookup failed | "
                    "research_id=%r | "
                    "company_id=%r",
                    research_id,
                    requested_company_id,
                )
                raise

        # =====================================================
        # 5. Apply database enrichment carefully
        # =====================================================

        if company_record is not None:
            database_data = self._company_model_to_dict(
                company_record
            )

            # Database data is useful enrichment, but we do not
            # blindly replace the research seed here.
            #
            # Canonical identity is established separately below.
            enriched = self._merge_database_data(
                base=enriched,
                database_data=database_data,
            )

            logger.info(
                "CompanyResearchService database record found | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "industry=%r",
                research_id,
                getattr(company_record, "id", None),
                getattr(company_record, "name", None),
                getattr(company_record, "ticker", None),
                getattr(company_record, "industry", None),
            )

        # =====================================================
        # 6. Establish canonical identity
        # =====================================================

        canonical_identity = self._build_canonical_identity(
            seed_data=company_data,
            database_record=company_record,
            enriched_data=enriched,
        )

        # =====================================================
        # 7. Validate canonical identity
        # =====================================================

        self._validate_canonical_identity(
            canonical_identity
        )

        # =====================================================
        # 8. Apply canonical identity immediately
        # =====================================================

        enriched = self._apply_canonical_identity(
            enriched,
            canonical_identity,
        )

        # =====================================================
        # 9. Search external providers
        # =====================================================

        provider_result = await self._search_providers(
            company_name=canonical_identity.get(
                "company_name"
            ),
            ticker=canonical_identity.get(
                "ticker"
            ),
            company_id=canonical_identity.get(
                "company_id"
            ),
            research_id=research_id,
        )

        # =====================================================
        # 10. Merge provider enrichment
        # =====================================================

        if provider_result:
            logger.info(
                "CompanyResearchService provider data found | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "fields=%s",
                research_id,
                canonical_identity.get("company_id"),
                canonical_identity.get("company_name"),
                canonical_identity.get("ticker"),
                sorted(provider_result.keys()),
            )

            enriched = self._merge_provider_data(
                base=enriched,
                provider_data=provider_result,
                canonical_identity=canonical_identity,
            )

        else:
            logger.warning(
                "CompanyResearchService no external provider "
                "data found | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r",
                research_id,
                canonical_identity.get("company_id"),
                canonical_identity.get("company_name"),
                canonical_identity.get("ticker"),
            )

        # =====================================================
        # 11. Re-apply canonical identity
        # =====================================================

        #
        # This is intentional.
        #
        # Even if a provider returns:
        #
        #     company_id = 999
        #     company_name = "Some Other Company"
        #     ticker = "ABC"
        #
        # those values cannot replace the canonical identity.
        #

        enriched = self._apply_canonical_identity(
            enriched,
            canonical_identity,
        )

        # =====================================================
        # 12. Normalize identity aliases
        # =====================================================

        enriched = self._normalize_identity(
            enriched
        )

        # Re-apply canonical identity after normalization as
        # another protection against accidental alias changes.
        enriched = self._apply_canonical_identity(
            enriched,
            canonical_identity,
        )

        # =====================================================
        # 13. Preserve research metadata
        # =====================================================

        metadata = enriched.get("metadata")

        if not isinstance(metadata, dict):
            metadata = {}

        metadata = dict(metadata)

        if research_id is not None:
            metadata["research_id"] = research_id

        if canonical_identity.get("company_id") is not None:
            metadata["company_id"] = canonical_identity.get(
                "company_id"
            )

        enriched["metadata"] = metadata

        # =====================================================
        # 14. Normalize sources
        # =====================================================

        enriched["sources"] = self._normalize_sources(
            enriched.get("sources")
        )

        # =====================================================
        # 15. Preserve canonical IDs at top level
        # =====================================================

        if canonical_identity.get("research_id") is not None:
            enriched["research_id"] = canonical_identity[
                "research_id"
            ]

        if canonical_identity.get("company_id") is not None:
            enriched["company_id"] = canonical_identity[
                "company_id"
            ]

        # =====================================================
        # 16. Final validation
        # =====================================================

        self._validate_final_result(
            enriched
        )

        logger.info(
            "CompanyResearchService completed | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r | "
            "sources=%s | "
            "fields=%s",
            enriched.get("research_id"),
            enriched.get("company_id"),
            enriched.get("company_name"),
            enriched.get("ticker"),
            enriched.get("industry"),
            enriched.get("sources"),
            sorted(enriched.keys()),
        )

        return enriched

    # =========================================================
    # Empty Value Detection
    # =========================================================

    @staticmethod
    def _is_empty_value(
        value: Any,
    ) -> bool:
        """
        Return True when a value represents missing/empty data.

        Empty values:

            None
            ""
            "   "
            []
            {}
            ()
            set()

        Important:

            0
            False

        are NOT considered empty because they may be legitimate
        values.
        """

        if value is None:
            return True

        if isinstance(value, str):
            return not value.strip()

        if isinstance(
            value,
            (list, tuple, set, dict),
        ):
            return len(value) == 0

        return False

    # =========================================================
    # Canonical Identity
    # =========================================================

    def _build_canonical_identity(
        self,
        seed_data: dict[str, Any],
        database_record: Any | None,
        enriched_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build canonical company identity.

        Priority:

            research_id:
                Research context

            company_id:
                Database Company.id
                >
                explicit research company_id

            company_name:
                Database Company.name
                >
                explicit research name

            ticker:
                Database Company.ticker
                >
                explicit research ticker

                NOTE:
                Ticker is optional and is NOT required for
                company research.

            industry:
                Company.industry
                >
                Company.sub_industry
                >
                Research.industry

        IMPORTANT:

        External provider data is NEVER used to establish
        canonical identity.
        """

        identity: dict[str, Any] = {}

        # -----------------------------------------------------
        # Research ID
        # -----------------------------------------------------

        identity["research_id"] = seed_data.get(
            "research_id"
        )

        # -----------------------------------------------------
        # Company ID
        # -----------------------------------------------------

        if database_record is not None:
            database_id = getattr(
                database_record,
                "id",
                None,
            )

            if database_id is not None:
                identity["company_id"] = database_id

        if identity.get("company_id") is None:
            identity["company_id"] = seed_data.get(
                "company_id"
            )

        if identity.get("company_id") is None:
            identity["company_id"] = enriched_data.get(
                "company_id"
            )

        # -----------------------------------------------------
        # Company name
        # -----------------------------------------------------

        if database_record is not None:
            database_name = getattr(
                database_record,
                "name",
                None,
            )

            if database_name:
                identity["company_name"] = (
                    database_name
                )

        if not identity.get("company_name"):
            identity["company_name"] = (
                seed_data.get("company_name")
                or seed_data.get("company")
                or seed_data.get("name")
                or enriched_data.get("company_name")
                or enriched_data.get("company")
                or enriched_data.get("name")
            )

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        # Ticker remains optional.
        #
        # If it exists in the database/research context,
        # preserve it for financial research.
        #
        # It is NOT required for company research.
        if database_record is not None:
            database_ticker = getattr(
                database_record,
                "ticker",
                None,
            )

            if database_ticker:
                identity["ticker"] = (
                    database_ticker
                )

        if not identity.get("ticker"):
            identity["ticker"] = (
                seed_data.get("ticker")
                or seed_data.get("symbol")
                or seed_data.get("stock_symbol")
                or enriched_data.get("ticker")
                or enriched_data.get("symbol")
                or enriched_data.get("stock_symbol")
            )

        # -----------------------------------------------------
        # Industry
        # -----------------------------------------------------
        #
        # CRITICAL ARCHITECTURAL RULE:
        #
        #     Company.industry
        #         >
        #     Company.sub_industry
        #         >
        #     Research.industry
        #
        # sector is NEVER used here.
        #

        database_industry = None
        database_sub_industry = None

        if database_record is not None:
            database_industry = getattr(
                database_record,
                "industry",
                None,
            )

            database_sub_industry = getattr(
                database_record,
                "sub_industry",
                None,
            )

        identity["industry"] = (
            database_industry
            or database_sub_industry
            or seed_data.get("industry")
            or enriched_data.get("industry")
        )

        # -----------------------------------------------------
        # Normalize identity values
        # -----------------------------------------------------

        if identity.get("company_id") is not None:
            try:
                identity["company_id"] = int(
                    identity["company_id"]
                )
            except (TypeError, ValueError):
                # Preserve non-integer IDs if the application
                # model uses another identifier type.
                pass

        if identity.get("company_name"):
            identity["company_name"] = (
                str(identity["company_name"])
                .strip()
            )

        if identity.get("ticker"):
            identity["ticker"] = (
                str(identity["ticker"])
                .strip()
                .upper()
            )

        if identity.get("industry"):
            identity["industry"] = (
                str(identity["industry"])
                .strip()
            )

        return identity

    # =========================================================
    # Canonical Identity Validation
    # =========================================================

    def _validate_canonical_identity(
        self,
        identity: dict[str, Any],
    ) -> None:
        """
        Validate that enough canonical company identity exists
        before external provider enrichment is attempted.

        Ticker is optional.
        """

        if not isinstance(identity, dict):
            raise TypeError(
                "Canonical company identity must be a dictionary."
            )

        company_id = identity.get(
            "company_id"
        )

        company_name = identity.get(
            "company_name"
        )

        # Ticker is intentionally NOT required.
        #
        # Company research can proceed with:
        #
        #   company_id
        #   OR
        #   company_name
        if not (
            company_id is not None
            or company_name
        ):
            raise ValueError(
                "CompanyResearchService could not establish "
                "canonical company identity. "
                "Expected company_id or company_name."
            )

    # =========================================================
    # Apply Canonical Identity
    # =========================================================

    def _apply_canonical_identity(
        self,
        data: dict[str, Any],
        canonical_identity: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Apply canonical identity to a company dictionary.

        Canonical identity ALWAYS wins.

        Ticker is applied only when one exists.
        """

        result = dict(data)

        research_id = canonical_identity.get(
            "research_id"
        )

        company_id = canonical_identity.get(
            "company_id"
        )

        company_name = canonical_identity.get(
            "company_name"
        )

        ticker = canonical_identity.get(
            "ticker"
        )

        industry = canonical_identity.get(
            "industry"
        )

        if research_id is not None:
            result["research_id"] = research_id

        if company_id is not None:
            result["company_id"] = company_id

        if company_name:
            result["company_name"] = company_name
            result["company"] = company_name
            result["name"] = company_name

        # Ticker is optional.
        if ticker:
            result["ticker"] = ticker

        if industry:
            result["industry"] = industry

        return result

    # =========================================================
    # Database Data Merge
    # =========================================================

    def _merge_database_data(
        self,
        base: dict[str, Any],
        database_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge database data into the research seed.

        Database identity is authoritative, but this method does
        not itself establish the final canonical identity.

        Existing explicit research metadata is preserved unless
        the field is missing or empty.
        """

        result = dict(base)

        for key, value in database_data.items():
            if value is None:
                continue

            # Database identity is resolved separately by
            # _build_canonical_identity().
            #
            # Do not blindly replace the research seed here.
            if key in {
                "id",
                "company_id",
                "name",
                "company_name",
                "ticker",
                "symbol",
                "stock_symbol",
                "industry",
                "sub_industry",
                "sector",
            }:
                existing = result.get(key)

                if self._is_empty_value(existing):
                    result[key] = value

                continue

            existing = result.get(key)

            if self._is_empty_value(existing):
                result[key] = value

        return result

    # =========================================================
    # Provider Search
    # =========================================================

    async def _search_providers(
        self,
        company_name: str | None,
        ticker: str | None,
        company_id: int | str | None,
        research_id: int | str | None,
    ) -> dict[str, Any]:
        """
        Query external company providers.

        IMPORTANT:

        Company research is NAME-FIRST.

        The provider search query is:

            company_name

        NOT:

            ticker or company_name

        This prevents provider discovery from failing because
        the database contains a market-specific ticker such as:

            D1EL34.SA

        Ticker is still supplied to the result-selection stage
        as an OPTIONAL secondary matching signal.

        Provider failure is non-fatal.
        """

        # -----------------------------------------------------
        # Company name is the primary provider query.
        # -----------------------------------------------------

        query = company_name

        if not query:
            logger.warning(
                "CompanyResearchService cannot search providers "
                "without company name | "
                "research_id=%r | "
                "company_id=%r",
                research_id,
                company_id,
            )
            return {}

        logger.info(
            "CompanyResearchService → PROVIDERS | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "query=%r",
            research_id,
            company_id,
            company_name,
            ticker,
            query,
        )

        try:
            results = await self._provider_manager_search(
                query=query
            )

        except Exception:
            logger.exception(
                "Company provider search failed | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "query=%r",
                research_id,
                company_id,
                company_name,
                query,
            )

            # External provider failure must never destroy
            # valid database/research identity.
            return {}

        if not results:
            return {}

        best_result = self._select_best_result(
            results=results,
            company_name=company_name,
            ticker=ticker,
        )

        if best_result is None:
            return {}

        model_data = self._object_to_dict(
            best_result
        )

        if not model_data:
            return {}

        # =====================================================
        # Process provider result
        # =====================================================

        try:
            processed = self.pipeline.process(
                model_data
            )

            # Support either a synchronous or asynchronous
            # pipeline implementation.
            if inspect.isawaitable(processed):
                processed = await processed

        except Exception:
            logger.exception(
                "Company provider processing failed | "
                "research_id=%r | "
                "company_id=%r",
                research_id,
                company_id,
            )

            # Raw provider data is still useful enrichment.
            return model_data

        if processed:
            processed_dict = self._object_to_dict(
                processed
            )

            if processed_dict:
                return processed_dict

        return model_data

    # =========================================================
    # Provider Manager Search
    # =========================================================

    async def _provider_manager_search(
        self,
        query: str,
    ) -> Any:
        """
        Call the canonical CompanyProviderManager search API.

        Preferred API:

            provider_manager.search(query=query)

        Compatibility fallbacks are included so that the service
        remains robust while provider-manager implementations are
        being migrated.

        IMPORTANT:

        These fallbacks are for CompanyProviderManager only.

        This service must never receive FinancialProviderManager.
        """

        search_method = getattr(
            self.provider_manager,
            "search",
            None,
        )

        if callable(search_method):
            result = search_method(
                query=query
            )

            if inspect.isawaitable(result):
                return await result

            return result

        # -----------------------------------------------------
        # Older API
        # -----------------------------------------------------

        search_company_method = getattr(
            self.provider_manager,
            "search_company",
            None,
        )

        if callable(search_company_method):
            result = search_company_method(
                query=query
            )

            if inspect.isawaitable(result):
                return await result

            return result

        # -----------------------------------------------------
        # Another possible API
        # -----------------------------------------------------

        search_companies_method = getattr(
            self.provider_manager,
            "search_companies",
            None,
        )

        if callable(search_companies_method):
            result = search_companies_method(
                query=query
            )

            if inspect.isawaitable(result):
                return await result

            return result

        raise AttributeError(
            "CompanyProviderManager does not expose a supported "
            "company search method. Expected one of: "
            "search(), search_company(), search_companies()."
        )

    # =========================================================
    # Best Provider Result
    # =========================================================

    def _select_best_result(
        self,
        results: Any,
        company_name: str | None,
        ticker: str | None,
    ) -> Any | None:
        """
        Select the provider result that best matches
        the requested company.

        Company research is NAME-FIRST.

        Priority:

            1. Exact company name
            2. Exact legal/company name
            3. Exact ticker, if available
            4. Provider ranking order

        Ticker is optional and is never required for
        company research.
        """

        if not results:
            return None

        if isinstance(results, dict):
            # A single provider result may be returned directly.
            results = [results]

        elif not isinstance(
            results,
            (list, tuple),
        ):
            results = [results]

        if not results:
            return None

        normalized_name = (
            self._normalize_string(company_name)
            if company_name
            else ""
        )

        normalized_ticker = (
            self._normalize_string(ticker)
            if ticker
            else ""
        )

        # =====================================================
        # Pass 1 — exact company name
        # =====================================================

        if normalized_name:
            for result in results:
                data = self._object_to_dict(
                    result
                )

                result_name = (
                    data.get("company_name")
                    or data.get("name")
                    or data.get("company")
                    or data.get("legal_name")
                )

                if not result_name:
                    continue

                if (
                    self._normalize_string(
                        str(result_name)
                    )
                    == normalized_name
                ):
                    return result

        # =====================================================
        # Pass 2 — exact ticker
        #
        # Ticker is only a secondary match.
        # =====================================================

        if normalized_ticker:
            for result in results:
                data = self._object_to_dict(
                    result
                )

                result_ticker = (
                    data.get("ticker")
                    or data.get("symbol")
                    or data.get("stock_symbol")
                )

                if not result_ticker:
                    continue

                if (
                    self._normalize_string(
                        str(result_ticker)
                    )
                    == normalized_ticker
                ):
                    return result

        # =====================================================
        # Pass 3 — provider-ranked first result
        # =====================================================

        return results[0]

    # =========================================================
    # Provider Data Merge
    # =========================================================

    def _merge_provider_data(
        self,
        base: dict[str, Any],
        provider_data: dict[str, Any],
        canonical_identity: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge provider information into canonical data.

        Provider values never overwrite canonical identity.

        Existing database/research values win.

        Missing values may be populated from the provider.
        """

        result = dict(base)

        if not provider_data:
            return result

        for key, value in provider_data.items():
            if value is None:
                continue

            # -------------------------------------------------
            # Canonical fields are protected.
            # -------------------------------------------------

            if key in self.CANONICAL_IDENTITY_FIELDS:
                continue

            # -------------------------------------------------
            # "id" is never accepted as provider company_id.
            # -------------------------------------------------

            if key == "id":
                continue

            # -------------------------------------------------
            # Sources need special handling.
            # -------------------------------------------------

            if key == "sources":
                result["sources"] = self._merge_sources(
                    result.get("sources"),
                    value,
                )
                continue

            # -------------------------------------------------
            # Singular source field.
            # -------------------------------------------------

            if key == "source":
                result["sources"] = self._merge_sources(
                    result.get("sources"),
                    value,
                )
                continue

            # -------------------------------------------------
            # Sector is useful provider metadata, but it is NOT
            # allowed to become canonical industry.
            # -------------------------------------------------

            if key == "sector":
                if self._is_empty_value(
                    result.get("sector")
                ):
                    result["sector"] = value

                continue

            # -------------------------------------------------
            # Fill missing values.
            # -------------------------------------------------

            existing = result.get(key)

            if self._is_empty_value(existing):
                result[key] = value
                continue

            # -------------------------------------------------
            # Existing application/database data wins.
            # -------------------------------------------------

            if key in self.PROVIDER_ENRICHMENT_FIELDS:
                continue

            # -------------------------------------------------
            # Unknown provider fields:
            #
            # Existing values win.
            # -------------------------------------------------

            continue

        # -----------------------------------------------------
        # Canonical identity always wins after merge.
        # -----------------------------------------------------

        return self._apply_canonical_identity(
            result,
            canonical_identity,
        )

    # =========================================================
    # Company Model → Dictionary
    # =========================================================

    def _company_model_to_dict(
        self,
        company: Any,
    ) -> dict[str, Any]:
        """
        Convert the Company ORM model into a dictionary.

        Only fields that actually exist on the model are copied.
        """

        result: dict[str, Any] = {}

        fields = (
            "id",
            "name",
            "legal_name",
            "ticker",
            "symbol",
            "stock_symbol",
            "cik",
            "lei",
            "industry",
            "sub_industry",
            "sector",
            "description",
            "website",
            "headquarters",
            "founded_year",
            "employees",
            "country",
            "exchange",
            "market_cap",
            "currency",
            "products",
            "executives",
            "shareholders",
            "operating_regions",
            "business_segments",
            "is_active",
        )

        for field_name in fields:
            if not hasattr(
                company,
                field_name,
            ):
                continue

            try:
                value = getattr(
                    company,
                    field_name,
                )

            except Exception:
                logger.debug(
                    "Failed reading Company.%s",
                    field_name,
                    exc_info=True,
                )
                continue

            if value is not None:
                result[field_name] = value

        # -----------------------------------------------------
        # Canonical ID
        # -----------------------------------------------------

        if result.get("id") is not None:
            result["company_id"] = result["id"]

        # -----------------------------------------------------
        # Canonical name
        # -----------------------------------------------------

        if result.get("name"):
            result["company_name"] = result["name"]

        return result

    # =========================================================
    # Generic Object → Dictionary
    # =========================================================

    def _object_to_dict(
        self,
        value: Any,
    ) -> dict[str, Any]:
        """
        Convert provider/model objects into dictionaries.
        """

        if value is None:
            return {}

        if isinstance(value, dict):
            return dict(value)

        # -----------------------------------------------------
        # Pydantic v2
        # -----------------------------------------------------

        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(model_dump):
            try:
                dumped = model_dump()

                if isinstance(
                    dumped,
                    dict,
                ):
                    return dumped

            except Exception:
                logger.debug(
                    "model_dump() failed",
                    exc_info=True,
                )

        # -----------------------------------------------------
        # Pydantic v1
        # -----------------------------------------------------

        dict_method = getattr(
            value,
            "dict",
            None,
        )

        if callable(dict_method):
            try:
                dumped = dict_method()

                if isinstance(
                    dumped,
                    dict,
                ):
                    return dumped

            except Exception:
                logger.debug(
                    "dict() failed",
                    exc_info=True,
                )

        # -----------------------------------------------------
        # Generic attribute extraction
        # -----------------------------------------------------

        result: dict[str, Any] = {}

        fields = (
            "id",
            "name",
            "company",
            "company_name",
            "legal_name",
            "ticker",
            "symbol",
            "stock_symbol",
            "cik",
            "lei",
            "industry",
            "sub_industry",
            "sector",
            "description",
            "website",
            "headquarters",
            "founded_year",
            "employees",
            "country",
            "exchange",
            "market_cap",
            "currency",
            "products",
            "executives",
            "shareholders",
            "operating_regions",
            "business_segments",
            "sources",
            "source",
            "confidence",
        )

        for field_name in fields:
            if not hasattr(
                value,
                field_name,
            ):
                continue

            try:
                field_value = getattr(
                    value,
                    field_name,
                )

            except Exception:
                logger.debug(
                    "Failed reading provider field %s",
                    field_name,
                    exc_info=True,
                )
                continue

            if field_value is not None:
                result[field_name] = field_value

        return result

    # =========================================================
    # Identity Normalization
    # =========================================================

    def _normalize_identity(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize company identity aliases.

        Canonical representation:

            company_id
            company_name
            company
            ticker
            industry

        Ticker is optional.

        Sector remains a separate field.
        """

        result = dict(data)

        company_name = (
            result.get("company_name")
            or result.get("name")
            or result.get("company")
        )

        ticker = (
            result.get("ticker")
            or result.get("symbol")
            or result.get("stock_symbol")
        )

        # IMPORTANT:
        #
        # sector is deliberately NOT used here.
        industry = result.get("industry")

        company_id = (
            result.get("company_id")
            or result.get("id")
        )

        if company_id is not None:
            result["company_id"] = company_id

        if company_name:
            company_name = str(
                company_name
            ).strip()

            result["company_name"] = company_name
            result["company"] = company_name

        # Ticker remains optional.
        if ticker:
            result["ticker"] = (
                str(ticker)
                .strip()
                .upper()
            )

        if industry:
            result["industry"] = (
                str(industry)
                .strip()
            )

        return result

    # =========================================================
    # Sources
    # =========================================================

    def _normalize_sources(
        self,
        sources: Any,
    ) -> list[Any]:
        """
        Normalize source information into a unique list.

        Supports:
            - None
            - string
            - list
            - tuple
            - set
            - individual source objects
        """

        if sources is None:
            return []

        if isinstance(
            sources,
            (list, tuple, set),
        ):
            values = list(sources)
        else:
            values = [sources]

        normalized: list[Any] = []

        for source in values:
            if source is None:
                continue

            if source not in normalized:
                normalized.append(source)

        return normalized

    def _merge_sources(
        self,
        existing: Any,
        incoming: Any,
    ) -> list[Any]:
        """
        Merge source collections without duplicates.
        """

        merged = self._normalize_sources(
            existing
        )

        incoming_sources = self._normalize_sources(
            incoming
        )

        for source in incoming_sources:
            if source not in merged:
                merged.append(source)

        return merged

    # =========================================================
    # Final Validation
    # =========================================================

    def _validate_final_result(
        self,
        data: dict[str, Any],
    ) -> None:
        """
        Validate the final enriched company record.

        Ticker is optional.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Final company research result must be a dictionary."
            )

        company_id = data.get(
            "company_id"
        )

        company_name = data.get(
            "company_name"
        )

        # Ticker is deliberately NOT used for validation.
        ticker = data.get(
            "ticker"
        )

        if not (
            company_id is not None
            or company_name
        ):
            raise ValueError(
                "CompanyResearchService could not resolve "
                "canonical company identity. "
                "Expected company_id or company_name."
            )

        # -----------------------------------------------------
        # Canonical alias consistency
        # -----------------------------------------------------

        if company_name:
            data["company_name"] = str(
                company_name
            ).strip()

            data["company"] = data[
                "company_name"
            ]

        # -----------------------------------------------------
        # Ticker normalization
        #
        # Optional; preserved when available.
        # -----------------------------------------------------

        if ticker:
            data["ticker"] = (
                str(ticker)
                .strip()
                .upper()
            )

        # -----------------------------------------------------
        # Industry normalization
        # -----------------------------------------------------

        if data.get("industry"):
            data["industry"] = (
                str(data["industry"])
                .strip()
            )

        # -----------------------------------------------------
        # Sources normalization
        # -----------------------------------------------------

        data["sources"] = self._normalize_sources(
            data.get("sources")
        )

    # =========================================================
    # String Normalization
    # =========================================================

    @staticmethod
    def _normalize_string(
        value: str | None,
    ) -> str:
        """
        Normalize strings for provider-result matching.
        """

        if not value:
            return ""

        return " ".join(
            str(value)
            .strip()
            .lower()
            .split()
        )

