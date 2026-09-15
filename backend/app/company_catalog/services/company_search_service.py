"""
Company Search Service.

Responsibilities
----------------
- Search the local company catalog first.
- Fall back to external company providers when needed.
- Normalize provider results through CompanyProcessingPipeline.
- Preserve existing company metadata through candidate matching.
- Upsert newly discovered companies.
- Merge local and imported results.
- Keep provider orchestration outside the repository layer.
"""

from __future__ import annotations

import inspect
import logging
from typing import Any, Sequence

from app.company_catalog.processing.normalizer import (
    CompanyNormalizer,
)
from app.company_catalog.processing.pipeline import (
    CompanyProcessingPipeline,
)
from app.company_catalog.providers.provider_manager import (
    CompanyProviderManager,
)
from app.db.models.company import Company
from app.repositories.company_repository import (
    CompanyRepository,
)


logger = logging.getLogger(__name__)


class CompanySearchService:
    """
    Hybrid company search service.

    Search strategy:

        PostgreSQL
            |
            | enough results
            v
          return

            |
            | insufficient results
            v
        External Providers
            |
            v
        Processing Pipeline
            |
            v
        Repository Upsert
            |
            v
        PostgreSQL
            |
            v
          merge
            |
            v
          return

    Individual provider failures are tolerated.
    Individual provider-company processing failures are also
    isolated so one bad external record does not abort the
    entire search.
    """

    def __init__(
        self,
        repository: CompanyRepository,
        provider_manager: CompanyProviderManager,
        pipeline: CompanyProcessingPipeline,
    ) -> None:
        self.repository = repository
        self.provider_manager = provider_manager
        self.pipeline = pipeline

    # =========================================================
    # SEARCH
    # =========================================================

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Company]:
        """
        Search the company catalog.

        Local PostgreSQL results are preferred.

        If the local database does not contain enough results,
        external providers are queried and the resulting records
        are normalized and upserted into PostgreSQL.

        The final result is deduplicated by Company.id.
        """

        query = (query or "").strip()

        if not query:
            return []

        try:
            limit = int(limit)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "limit must be an integer."
            ) from exc

        try:
            offset = int(offset)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "offset must be an integer."
            ) from exc

        limit = max(
            1,
            min(limit, 100),
        )

        offset = max(
            0,
            offset,
        )

        logger.info(
            "Company search started | query=%r | limit=%d | offset=%d",
            query,
            limit,
            offset,
        )

        # -----------------------------------------------------
        # 1. LOCAL DATABASE
        # -----------------------------------------------------

        local_results = await self.repository.search(
            query=query,
            limit=limit,
            offset=offset,
        )

        local_results = list(local_results or [])

        logger.info(
            "Company local search | query=%r | results=%d",
            query,
            len(local_results),
        )

        # If the local database already has enough records,
        # there is no reason to contact external providers.
        if len(local_results) >= limit:
            return local_results[:limit]

        # -----------------------------------------------------
        # 2. PROVIDER SEARCH
        # -----------------------------------------------------

        try:
            provider_results = await self.provider_manager.search(
                query=query,
            )

        except Exception:
            logger.exception(
                "Company provider search failed | query=%r",
                query,
            )

            return local_results[:limit]

        if not provider_results:
            logger.info(
                "No external company provider results | query=%r",
                query,
            )

            return local_results[:limit]

        logger.info(
            "Company provider search | query=%r | results=%d",
            query,
            len(provider_results),
        )

        # -----------------------------------------------------
        # 3. PROCESS PROVIDER RESULTS
        # -----------------------------------------------------

        imported: list[Company] = []

        for provider_company in provider_results:
            if not isinstance(provider_company, dict):
                continue

            try:
                # -------------------------------------------------
                # Find matching local candidates.
                #
                # Candidate lookup is helpful for preserving
                # existing metadata, but a candidate lookup
                # failure should not necessarily destroy the
                # external search result.
                # -------------------------------------------------

                candidates: Sequence[Company] = []

                try:
                    candidates = (
                        await self.repository.find_candidates(
                            provider_company
                        )
                    )
                except Exception:
                    logger.exception(
                        "Company candidate lookup failed | "
                        "company=%r",
                        provider_company,
                    )

                candidate_dicts = [
                    self._company_to_dict(candidate)
                    for candidate in (candidates or [])
                ]

                # -------------------------------------------------
                # Run company normalization / processing.
                # -------------------------------------------------

                processed = self.pipeline.process(
                    provider_company,
                    candidates=candidate_dicts,
                )

                # Support both synchronous and asynchronous
                # pipeline implementations.
                if inspect.isawaitable(processed):
                    processed = await processed

                if not processed:
                    logger.debug(
                        "Company pipeline returned no record | "
                        "company=%r",
                        provider_company,
                    )
                    continue

                if not isinstance(processed, dict):
                    logger.warning(
                        "Company pipeline returned invalid result | "
                        "type=%s | company=%r",
                        type(processed).__name__,
                        provider_company,
                    )
                    continue

                # -------------------------------------------------
                # Persist normalized company.
                # -------------------------------------------------

                saved = await self.repository.upsert(
                    processed
                )

                if saved is None:
                    logger.warning(
                        "Company repository upsert returned None | "
                        "company=%r",
                        processed,
                    )
                    continue

                imported.append(saved)

            except Exception:
                logger.exception(
                    "Failed to process provider company | "
                    "query=%r | company=%r",
                    query,
                    provider_company,
                )

        # -----------------------------------------------------
        # 4. MERGE LOCAL + IMPORTED RESULTS
        # -----------------------------------------------------

        merged: dict[int, Company] = {}

        for company in local_results:
            if company is None:
                continue

            company_id = getattr(
                company,
                "id",
                None,
            )

            if company_id is None:
                continue

            merged[company_id] = company

        for company in imported:
            if company is None:
                continue

            company_id = getattr(
                company,
                "id",
                None,
            )

            if company_id is None:
                continue

            merged[company_id] = company

        results = list(
            merged.values()
        )

        # -----------------------------------------------------
        # 5. RESULT LIMIT
        # -----------------------------------------------------

        results = results[:limit]

        logger.info(
            "Company search finished | "
            "query=%r | local=%d | imported=%d | final=%d",
            query,
            len(local_results),
            len(imported),
            len(results),
        )

        return results

    # =========================================================
    # GET COMPANY
    # =========================================================

    async def get_company(
        self,
        company_id: int,
    ) -> Company | None:
        """
        Retrieve a company by database ID.
        """

        return await self.repository.get_by_id(
            company_id
        )

    # =========================================================
    # MODEL -> DICT
    # =========================================================

    @staticmethod
    def _company_to_dict(
        company: Company,
    ) -> dict[str, Any]:
        """
        Convert a Company SQLAlchemy model into a provider/pipeline
        compatible dictionary.

        The conversion is based on the actual SQLAlchemy table
        columns so newly added Company columns are automatically
        included.
        """

        result: dict[str, Any] = {}

        for column in Company.__table__.columns:
            value = getattr(
                company,
                column.name,
                None,
            )

            result[column.name] = value

        # -----------------------------------------------------
        # Canonical company ID aliases
        # -----------------------------------------------------

        company_id = result.get("id")

        if company_id is not None:
            result["company_id"] = company_id

        # -----------------------------------------------------
        # Canonical company-name aliases
        # -----------------------------------------------------

        name = result.get("name")

        if name:
            result["company_name"] = name
            result["company"] = name

            result["normalized_name"] = (
                CompanyNormalizer.normalize_name_for_matching(
                    name
                )
            )

        # -----------------------------------------------------
        # Canonical ticker aliases
        # -----------------------------------------------------

        ticker = result.get("ticker")

        if ticker:
            result["symbol"] = ticker

        return result


__all__ = [
    "CompanySearchService",
]