from __future__ import annotations

import asyncio
import logging

from repositories.company_repository import CompanyRepository
from services.company_search_service import CompanySearchService

logger = logging.getLogger(__name__)


class CompanySyncTask:
    """
    Synchronizes company information from external providers
    into the local database.
    """

    def __init__(self) -> None:
        self.search_service = CompanySearchService()
        self.repository = CompanyRepository()

    async def sync_company(self, query: str) -> int:
        """
        Search for a company and save/update it locally.

        Returns:
            Number of companies synchronized.
        """

        logger.info("Sync started for '%s'", query)

        companies = await self.search_service.search(query)

        count = 0

        for company in companies:
            await self.repository.upsert(company)
            count += 1

        logger.info("Synchronized %d companies.", count)

        return count

    async def sync_multiple(
        self,
        queries: list[str],
    ) -> dict[str, int]:
        """
        Synchronize multiple companies concurrently.
        """

        tasks = [
            self.sync_company(query)
            for query in queries
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        output: dict[str, int] = {}

        for query, result in zip(queries, results):
            if isinstance(result, Exception):
                logger.exception(
                    "Failed to sync '%s'",
                    query,
                )
                output[query] = 0
            else:
                output[query] = result

        return output

    async def sync_popular_companies(self) -> None:
        """
        Periodically synchronize frequently searched companies.
        """

        popular = [
            "Apple",
            "Microsoft",
            "NVIDIA",
            "Amazon",
            "Alphabet",
            "Meta",
            "Tesla",
        ]

        await self.sync_multiple(popular)


async def run_company_sync() -> None:
    """
    Entry point for scheduled jobs.
    """

    task = CompanySyncTask()
    await task.sync_popular_companies()


if __name__ == "__main__":
    asyncio.run(run_company_sync())