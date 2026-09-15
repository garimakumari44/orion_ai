"""
app/company_catalog/service.py

Company Catalog Service.

Coordinates:

    ProviderManager
          |
          v
    ProcessingPipeline
          |
          v
    CompanyRepository
          |
          v
      PostgreSQL
"""

from __future__ import annotations

import logging
from typing import Any

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


class CompanyCatalogService:
    """
    Application service for company catalog operations.
    """

    def __init__(
        self,
        repository: CompanyRepository,
        provider_manager: CompanyProviderManager,
        processing_pipeline: CompanyProcessingPipeline,
    ) -> None:

        if repository is None:
            raise ValueError(
                "CompanyRepository is required."
            )

        if provider_manager is None:
            raise ValueError(
                "CompanyProviderManager is required."
            )

        if processing_pipeline is None:
            raise ValueError(
                "CompanyProcessingPipeline is required."
            )

        self.repository = repository
        self.provider_manager = provider_manager
        self.processing_pipeline = processing_pipeline

    # =========================================================
    # SEARCH / IMPORT
    # =========================================================

    async def search_or_import(
        self,
        query: str,
    ) -> list[Company]:

        if not isinstance(
            query,
            str,
        ):
            raise TypeError(
                "Company search query must be a string."
            )

        query = query.strip()

        if not query:
            return []

        # -----------------------------------------------------
        # LOCAL
        # -----------------------------------------------------

        existing = await self.repository.search(
            query=query,
            limit=10,
            offset=0,
        )

        if existing:
            return existing

        # -----------------------------------------------------
        # EXTERNAL PROVIDERS
        # -----------------------------------------------------

        try:

            raw_companies = (
                await self.provider_manager.search(
                    query=query
                )
            )

        except Exception:

            logger.exception(
                "External company search failed | query=%r",
                query,
            )

            return []

        if not raw_companies:
            return []

        companies: list[Company] = []

        # -----------------------------------------------------
        # PROCESS + UPSERT
        # -----------------------------------------------------

        for raw_company in raw_companies:

            if not isinstance(
                raw_company,
                dict,
            ):
                continue

            try:

                enriched = (
                    await self._enrich_provider_result(
                        raw_company
                    )
                )

                candidates = (
                    await self.repository.find_candidates(
                        enriched
                    )
                )

                processed = (
                    self.processing_pipeline.process(
                        enriched,
                        candidates=[
                            self._company_to_dict(
                                candidate
                            )
                            for candidate in candidates
                        ],
                    )
                )

                if not processed:
                    continue

                company = await self.repository.upsert(
                    processed
                )

                companies.append(
                    company
                )

            except Exception:

                logger.exception(
                    "Company catalog processing failed | "
                    "query=%r | company=%r",
                    query,
                    raw_company,
                )

        return companies

    # =========================================================
    # CREATE
    # =========================================================

    async def create_company(
        self,
        data: dict[str, Any],
    ) -> Company:

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Company data must be a dictionary."
            )

        if not data:
            raise ValueError(
                "Company data is required."
            )

        enriched = (
            await self._enrich_provider_result(
                data
            )
        )

        candidates = (
            await self.repository.find_candidates(
                enriched
            )
        )

        processed = (
            self.processing_pipeline.process(
                enriched,
                candidates=[
                    self._company_to_dict(
                        candidate
                    )
                    for candidate in candidates
                ],
            )
        )

        return await self.repository.create(
            processed
        )

    # =========================================================
    # UPSERT
    # =========================================================

    async def upsert_company(
        self,
        data: dict[str, Any],
    ) -> Company:

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Company data must be a dictionary."
            )

        enriched = (
            await self._enrich_provider_result(
                data
            )
        )

        candidates = (
            await self.repository.find_candidates(
                enriched
            )
        )

        processed = (
            self.processing_pipeline.process(
                enriched,
                candidates=[
                    self._company_to_dict(
                        candidate
                    )
                    for candidate in candidates
                ],
            )
        )

        return await self.repository.upsert(
            processed
        )

    # =========================================================
    # UPDATE
    # =========================================================

    async def update_company(
        self,
        company: Company,
        data: dict[str, Any],
    ) -> Company:

        if company is None:
            raise ValueError(
                "Company is required."
            )

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Company data must be a dictionary."
            )

        company_id = getattr(
            company,
            "id",
            None,
        )

        if company_id is None:
            raise ValueError(
                "Company must have a valid database ID."
            )

        update_data = dict(data)

        update_data["company_id"] = company_id
        update_data["id"] = company_id

        # Preserve existing classification.
        for field in (
            "sector",
            "industry",
            "sub_industry",
        ):

            if field not in update_data:

                existing = getattr(
                    company,
                    field,
                    None,
                )

                if existing:
                    update_data[field] = existing

        processed = (
            self.processing_pipeline.process(
                update_data,
                candidates=[
                    self._company_to_dict(
                        company
                    )
                ],
            )
        )

        return await self.repository.update(
            company_id,
            processed,
        )

    # =========================================================
    # GET
    # =========================================================

    async def get_company(
        self,
        company_id: int,
    ) -> Company | None:

        return await self.repository.get_by_id(
            company_id
        )

    # =========================================================
    # ENRICHMENT
    # =========================================================

    async def _enrich_provider_result(
        self,
        company_data: dict[str, Any],
    ) -> dict[str, Any]:

        enriched = dict(
            company_data
        )

        symbol = (
            enriched.get("ticker")
            or enriched.get("symbol")
            or enriched.get("stock_symbol")
        )

        if not symbol:
            return enriched

        try:

            profile = (
                await self.provider_manager
                .get_company_profile(
                    str(symbol).strip()
                )
            )

        except Exception:

            logger.warning(
                "Company profile enrichment failed | "
                "symbol=%r",
                symbol,
                exc_info=True,
            )

            return enriched

        if not isinstance(
            profile,
            dict,
        ):
            return enriched

        for field, value in profile.items():

            if self._has_value(value):
                enriched[field] = value

        return enriched

    # =========================================================
    # MODEL -> DICT
    # =========================================================

    @staticmethod
    def _company_to_dict(
        company: Company,
    ) -> dict[str, Any]:

        if company is None:
            return {}

        result: dict[str, Any] = {}

        for column in Company.__table__.columns:

            try:

                result[column.name] = getattr(
                    company,
                    column.name,
                    None,
                )

            except Exception:

                continue

        company_id = result.get("id")

        if company_id is not None:
            result["id"] = company_id
            result["company_id"] = company_id

        name = result.get("name")

        if name:
            result["company_name"] = name
            result["company"] = name

        ticker = result.get("ticker")

        if ticker:
            result["ticker"] = ticker
            result["symbol"] = ticker

        return result

    # =========================================================
    # VALUE CHECK
    # =========================================================

    @staticmethod
    def _has_value(
        value: Any,
    ) -> bool:

        if value is None:
            return False

        if isinstance(
            value,
            str,
        ):
            return bool(value.strip())

        if isinstance(
            value,
            (
                list,
                tuple,
                set,
                dict,
            ),
        ):
            return bool(value)

        return True