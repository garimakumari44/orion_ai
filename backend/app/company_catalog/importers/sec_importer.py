"""
app/company_catalog/importer/sec_importer.py

SEC Company Catalog Importer.

SEC is used as the canonical company identity/master-data source.

Source:
    https://www.sec.gov/files/company_tickers.json

Primary fields:

    - company name
    - ticker
    - CIK

SEC company_tickers.json does not provide reliable
sector / industry classification.

Therefore this importer does not invent classification data.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.company_catalog.processing.deduplicate import (
    CompanyDeduplicator,
)
from app.company_catalog.processing.pipeline import (
    CompanyProcessingPipeline,
)
from app.repositories.company_repository import (
    CompanyRepository,
)

logger = logging.getLogger(__name__)


class SECImporter:
    """
    Import SEC company master data into PostgreSQL.
    """

    SEC_URL = (
        "https://www.sec.gov/files/company_tickers.json"
    )

    HEADERS = {
        "User-Agent": (
            "OrionAI research platform "
            "contact@example.com"
        )
    }

    def __init__(
        self,
        repository: CompanyRepository,
    ) -> None:

        if repository is None:
            raise ValueError(
                "CompanyRepository is required."
            )

        self.repository = repository

        self.pipeline = CompanyProcessingPipeline(
            deduplicator=CompanyDeduplicator()
        )

    # =========================================================
    # FETCH
    # =========================================================

    async def fetch_companies(
        self,
    ) -> list[dict[str, Any]]:

        async with httpx.AsyncClient(
            timeout=30.0,
            headers=self.HEADERS,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                self.SEC_URL
            )

            response.raise_for_status()

            data = response.json()

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "SEC company ticker response must "
                "be a JSON object."
            )

        companies: list[dict[str, Any]] = []

        for item in data.values():

            if not isinstance(
                item,
                dict,
            ):
                continue

            name = item.get("title")
            ticker = item.get("ticker")
            cik = item.get("cik_str")

            if not name and not ticker:
                continue

            company = {
                "name": name,
                "ticker": ticker,
                "source": "sec",
            }

            if cik is not None:

                company["cik"] = str(
                    cik
                ).strip()

            companies.append(
                company
            )

        logger.info(
            "SEC company catalog downloaded | count=%d",
            len(companies),
        )

        return companies

    # =========================================================
    # IMPORT
    # =========================================================

    async def import_companies(
        self,
        limit: int | None = None,
    ) -> int:

        companies = await self.fetch_companies()

        if limit is not None:

            if limit <= 0:
                raise ValueError(
                    "limit must be greater than zero."
                )

            companies = companies[:limit]

        imported = 0

        for company_data in companies:

            try:

                processed = self.pipeline.process(
                    company_data
                )

                if not processed:
                    continue

                await self.repository.upsert(
                    processed
                )

                imported += 1

            except Exception:

                logger.exception(
                    "SEC company import failed | "
                    "name=%r | ticker=%r | cik=%r",
                    company_data.get("name"),
                    company_data.get("ticker"),
                    company_data.get("cik"),
                )

        logger.info(
            "SEC company import completed | "
            "processed=%d | total=%d",
            imported,
            len(companies),
        )

        return imported