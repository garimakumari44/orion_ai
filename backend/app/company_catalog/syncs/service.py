from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.company_catalog.processing.pipeline import CompanyProcessingPipeline
from app.company_catalog.providers.manager import ProviderManager
from app.company_catalog.repositories.company_repository import CompanyRepository
from app.company_catalog.sync.statistics import SyncStatistics

logger = logging.getLogger(__name__)


class CompanySyncService:
    """
    Synchronizes the company catalog from all configured providers.

    Responsibilities
    ----------------
    - Iterate over providers
    - Download company batches
    - Process company data
    - Persist changes
    - Collect synchronization statistics

    This service intentionally contains no provider-specific logic.
    """

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db
        self.repository = CompanyRepository(db)
        self.provider_manager = ProviderManager()
        self.statistics = SyncStatistics()

    async def synchronize(
        self,
        batch_size: int = 500,
    ) -> SyncStatistics:
        """
        Synchronize companies from every enabled provider.

        Returns:
            SyncStatistics
        """

        providers = self.provider_manager.get_providers()

        logger.info(
            "Starting company synchronization (%d providers)",
            len(providers),
        )

        for provider in providers:

            logger.info(
                "Synchronizing provider: %s",
                provider.name,
            )

            offset = 0

            while True:

                try:

                    companies = await provider.list_companies(
                        limit=batch_size,
                        offset=offset,
                    )

                except Exception:
                    logger.exception(
                        "Provider %s failed while fetching companies.",
                        provider.name,
                    )
                    self.statistics.mark_provider_failed(provider.name)
                    break

                if not companies:
                    break

                for raw_company in companies:

                    await self._process_company(
                        provider.name,
                        raw_company,
                    )

                offset += batch_size

        logger.info("Company synchronization completed.")

        return self.statistics

    async def _process_company(
        self,
        provider_name: str,
        raw_company: dict[str, Any],
    ) -> None:
        """
        Process and persist a single company.
        """

        try:

            candidates = await self.repository.find_candidates(
                raw_company,
            )

            processed = CompanyProcessingPipeline.process(
                raw_company,
                candidates,
            )

            result = await self.repository.upsert(
                processed,
            )

            self.statistics.record(result)

        except Exception:

            logger.exception(
                "Failed processing company from %s",
                provider_name,
            )

            self.statistics.mark_failed()