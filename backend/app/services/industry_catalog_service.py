"""
app/services/industry_catalog_service.py

Industry Catalog Service.

Responsibilities
----------------
- Provide the application-facing API for industry catalog data.
- Coordinate repository persistence.
- Coordinate industry metadata processing.
- Keep provider access behind the processing/catalog layer.
- Normalize industry metadata before persistence.
- Provide lookup, search, create, update, delete and upsert operations.
- Resolve canonical industry records for research services.

Architecture:

    ResearchService
            |
            v
    IndustryCatalogService
            |
        +---+----------------+
        |                    |
        v                    v
    Repository        ProcessingPipeline
                             |
                             v
                    IndustryProviderManager

IMPORTANT
---------
The processing/enrichment layer may carry company context:

    company
    ticker
    company_id
    sector
    sub_industry

That context is useful to providers and resolution logic.

It is NOT automatically Industry persistence data.

Industry invariant
------------------
    sector != industry

Sector is NEVER promoted to industry.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from app.industry_catalog.processing.pipeline import (
    IndustryProcessingPipeline,
)
from app.industry_catalog.repository import IndustryRepository


class IndustryCatalogService:
    """
    Application service for the Industry Catalog.

    Coordinates:

        Repository
             +
        Processing Pipeline
    """

    def __init__(
        self,
        repository: IndustryRepository,
        processing_pipeline: IndustryProcessingPipeline,
    ) -> None:

        if repository is None:
            raise ValueError(
                "IndustryRepository is required."
            )

        if processing_pipeline is None:
            raise ValueError(
                "IndustryProcessingPipeline is required."
            )

        self.repository = repository
        self.processing_pipeline = processing_pipeline

    # ==================================================================
    # GET BY ID
    # ==================================================================

    async def get_by_id(
        self,
        industry_id: int,
    ) -> Any | None:

        return await self.repository.get_by_id(
            industry_id
        )

    # ==================================================================
    # GET BY CODE
    # ==================================================================

    async def get_by_code(
        self,
        code: str,
    ) -> Any | None:

        normalized_code = self._clean_string(code)

        if not normalized_code:
            return None

        return await self.repository.get_by_code(
            normalized_code
        )

    # ==================================================================
    # GET BY INDUSTRY
    # ==================================================================

    async def get_by_industry(
        self,
        industry: str,
    ) -> Any | None:

        normalized_industry = self._clean_string(
            industry
        )

        if not normalized_industry:
            return None

        return await self.repository.get_by_industry(
            normalized_industry
        )

    # ==================================================================
    # LIST ALL
    # ==================================================================

    async def list_all(
        self,
    ) -> list[Any]:

        return await self.repository.list_all()

    # ==================================================================
    # SEARCH
    # ==================================================================

    async def search(
        self,
        query: str,
    ) -> list[Any]:

        normalized_query = self._clean_string(
            query
        )

        if not normalized_query:
            return await self.repository.list_all()

        return await self.repository.search(
            normalized_query
        )

    # ==================================================================
    # RESOLVE
    # ==================================================================

    async def resolve(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        company_record: Any | None = None,
        company_id: int | None = None,
        **kwargs: Any,
    ) -> Any | None:
        """
        Resolve a canonical industry record.

        Resolution priority:

            1. Company.industry
            2. Company.sub_industry
            3. Explicit/request industry
            4. Existing catalog lookup
            5. Classification-code lookup
            6. Provider enrichment
            7. Canonical upsert

        Sector is NEVER treated as industry.
        """

        # --------------------------------------------------------------
        # Resolve identity from company record
        # --------------------------------------------------------------

        if company_record is not None:

            company_id = (
                getattr(
                    company_record,
                    "id",
                    None,
                )
                or getattr(
                    company_record,
                    "company_id",
                    None,
                )
                or company_id
            )

            company = (
                self._clean_string(
                    getattr(
                        company_record,
                        "name",
                        None,
                    )
                )
                or self._clean_string(
                    getattr(
                        company_record,
                        "company",
                        None,
                    )
                )
                or self._clean_string(
                    getattr(
                        company_record,
                        "company_name",
                        None,
                    )
                )
                or company
            )

            ticker = (
                self._clean_string(
                    getattr(
                        company_record,
                        "ticker",
                        None,
                    )
                )
                or ticker
            )

        normalized_company = self._clean_string(
            company
        )

        normalized_ticker = self._normalize_ticker(
            ticker
        )

        normalized_industry = self._clean_string(
            industry
        )

        # --------------------------------------------------------------
        # Extract company classifications
        # --------------------------------------------------------------

        company_industry: str | None = None
        company_sub_industry: str | None = None
        company_sector: str | None = None

        if company_record is not None:

            company_industry = self._clean_string(
                getattr(
                    company_record,
                    "industry",
                    None,
                )
            )

            company_sub_industry = self._clean_string(
                getattr(
                    company_record,
                    "sub_industry",
                    None,
                )
            )

            company_sector = self._clean_string(
                getattr(
                    company_record,
                    "sector",
                    None,
                )
            )

        # --------------------------------------------------------------
        # Build enrichment kwargs once
        # --------------------------------------------------------------

        resolution_kwargs = dict(kwargs)

        for key in (
            "company",
            "ticker",
            "industry",
            "company_record",
            "company_id",
            "sub_industry",
            "sector",
        ):
            resolution_kwargs.pop(
                key,
                None,
            )

        if company_record is not None:
            resolution_kwargs["company_record"] = (
                company_record
            )

        if company_id is not None:
            resolution_kwargs["company_id"] = (
                company_id
            )

        if company_sub_industry:
            resolution_kwargs["sub_industry"] = (
                company_sub_industry
            )

        if company_sector:
            resolution_kwargs["sector"] = (
                company_sector
            )

        # --------------------------------------------------------------
        # Candidate industry
        # --------------------------------------------------------------

        candidate_industry = (
            company_industry
            or normalized_industry
        )

        # --------------------------------------------------------------
        # 1. Existing canonical company industry
        # --------------------------------------------------------------

        if candidate_industry:

            existing = await self.get_by_industry(
                candidate_industry
            )

            if existing is not None:
                return existing

        # --------------------------------------------------------------
        # 2. Company sub-industry
        # --------------------------------------------------------------

        if company_sub_industry:

            existing = await self.get_by_industry(
                company_sub_industry
            )

            if existing is not None:
                return existing

        # --------------------------------------------------------------
        # 3. Classification-code lookup
        # --------------------------------------------------------------

        classification_code_keys = (
            "gics_code",
            "naics_code",
            "sic_code",
            "icb_code",
            "industry_code",
            "classification_code",
            "code",
        )

        for key in classification_code_keys:

            code = resolution_kwargs.get(key)

            if code is None:
                continue

            normalized_code = self._clean_string(
                code
            )

            if not normalized_code:
                continue

            existing = await self.get_by_code(
                normalized_code
            )

            if existing is not None:
                return existing

        # --------------------------------------------------------------
        # 4. Provider enrichment
        # --------------------------------------------------------------

        if normalized_company or normalized_ticker:

            enriched = await self.enrich(
                company=normalized_company,
                ticker=normalized_ticker,
                industry=candidate_industry,
                **resolution_kwargs,
            )

            if not isinstance(
                enriched,
                dict,
            ):
                raise TypeError(
                    "Industry enrichment must return "
                    "a dictionary."
                )

            enriched_industry = self._extract_industry(
                enriched
            )

            if not enriched_industry:
                raise ValueError(
                    "Industry provider enrichment "
                    "completed without producing a "
                    "canonical industry. "
                    f"company={normalized_company!r} "
                    f"ticker={normalized_ticker!r}"
                )

            enriched_payload = dict(
                enriched
            )

            enriched_payload["industry"] = (
                enriched_industry
            )

            if (
                normalized_company
                and not enriched_payload.get("company")
            ):
                enriched_payload["company"] = (
                    normalized_company
                )

            if (
                normalized_ticker
                and not enriched_payload.get("ticker")
            ):
                enriched_payload["ticker"] = (
                    normalized_ticker
                )

            if (
                company_id is not None
                and not enriched_payload.get("company_id")
            ):
                enriched_payload["company_id"] = (
                    company_id
                )

            if (
                company_sector
                and not enriched_payload.get("sector")
            ):
                enriched_payload["sector"] = (
                    company_sector
                )

            if (
                company_sub_industry
                and not enriched_payload.get(
                    "sub_industry"
                )
            ):
                enriched_payload["sub_industry"] = (
                    company_sub_industry
                )

            return await self.upsert(
                enriched_payload
            )

        # --------------------------------------------------------------
        # 5. Nothing available
        # --------------------------------------------------------------

        return None

    # ==================================================================
    # CREATE
    # ==================================================================

    async def create(
        self,
        data: dict[str, Any],
    ) -> Any:

        processed = await self._process(data)

        processed = self._ensure_canonical_identifiers(
            processed
        )

        return await self.repository.create(
            processed
        )

    # ==================================================================
    # UPDATE
    # ==================================================================

    async def update(
        self,
        industry_id: int,
        data: dict[str, Any],
    ) -> Any | None:

        processed = await self._process(data)

        processed = self._ensure_canonical_identifiers(
            processed,
            preserve_existing_code=True,
        )

        return await self.repository.update(
            industry_id,
            processed,
        )

    # ==================================================================
    # DELETE
    # ==================================================================

    async def delete(
        self,
        industry_id: int,
    ) -> bool:

        return await self.repository.delete(
            industry_id
        )

    # ==================================================================
    # UPSERT
    # ==================================================================

    async def upsert(
        self,
        data: dict[str, Any],
    ) -> Any:

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Industry catalog data must "
                "be a dictionary."
            )

        industry = self._extract_industry(
            data
        )

        if not industry:
            raise ValueError(
                "Cannot upsert industry catalog "
                "record without a canonical industry."
            )

        payload = dict(data)

        payload["industry"] = industry

        processed = await self._process(
            payload
        )

        # --------------------------------------------------------------
        # CRITICAL FIX
        #
        # The provider is allowed to return only:
        #
        #     industry = "Software - Application"
        #
        # but the database requires:
        #
        #     code IS NOT NULL
        #
        # Therefore the service creates a deterministic canonical code
        # when no real classification code was provided.
        # --------------------------------------------------------------

        processed = self._ensure_canonical_identifiers(
            processed
        )

        return await self.repository.upsert(
            processed
        )

    # ==================================================================
    # PROCESS
    # ==================================================================

    async def process(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        return await self._process(data)

    # ==================================================================
    # ENRICH
    # ==================================================================

    async def enrich(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        company_record: Any | None = None,
        company_id: int | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Acquire and process industry metadata.

        Company/ticker/company_id remain available to the provider.
        """

        normalized_company = self._clean_string(
            company
        )

        normalized_ticker = self._normalize_ticker(
            ticker
        )

        normalized_industry = self._clean_string(
            industry
        )

        pipeline_kwargs = dict(kwargs)

        for key in (
            "company",
            "ticker",
            "industry",
            "company_record",
            "company_id",
        ):
            pipeline_kwargs.pop(
                key,
                None,
            )

        if company_record is not None:
            pipeline_kwargs.setdefault(
                "company_record",
                company_record,
            )

        if company_id is not None:
            pipeline_kwargs.setdefault(
                "company_id",
                company_id,
            )

        result = await self.processing_pipeline.enrich(
            company=normalized_company,
            ticker=normalized_ticker,
            industry=normalized_industry,
            **pipeline_kwargs,
        )

        if not isinstance(
            result,
            dict,
        ):
            raise TypeError(
                "IndustryProcessingPipeline.enrich() "
                "must return a dictionary."
            )

        return result

    # ==================================================================
    # GET OR ENRICH
    # ==================================================================

    async def get_or_enrich(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        company_record: Any | None = None,
        company_id: int | None = None,
        **kwargs: Any,
    ) -> Any:

        normalized_company = self._clean_string(
            company
        )

        normalized_ticker = self._normalize_ticker(
            ticker
        )

        normalized_industry = self._clean_string(
            industry
        )

        if normalized_industry:

            existing = await self.get_by_industry(
                normalized_industry
            )

            if existing is not None:
                return existing

        enriched = await self.enrich(
            company=normalized_company,
            ticker=normalized_ticker,
            industry=normalized_industry,
            company_record=company_record,
            company_id=company_id,
            **kwargs,
        )

        if not isinstance(
            enriched,
            dict,
        ):
            raise TypeError(
                "Industry enrichment must return "
                "a dictionary."
            )

        enriched_industry = self._extract_industry(
            enriched
        )

        if not enriched_industry:
            raise ValueError(
                "Industry enrichment did not produce "
                "a canonical industry. "
                f"company={normalized_company!r} "
                f"ticker={normalized_ticker!r}"
            )

        enriched_payload = dict(
            enriched
        )

        enriched_payload["industry"] = (
            enriched_industry
        )

        if (
            normalized_company
            and not enriched_payload.get("company")
        ):
            enriched_payload["company"] = (
                normalized_company
            )

        if (
            normalized_ticker
            and not enriched_payload.get("ticker")
        ):
            enriched_payload["ticker"] = (
                normalized_ticker
            )

        if (
            company_id is not None
            and not enriched_payload.get("company_id")
        ):
            enriched_payload["company_id"] = (
                company_id
            )

        return await self.upsert(
            enriched_payload
        )

    # ==================================================================
    # PRIVATE PROCESSING
    # ==================================================================

    async def _process(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Industry catalog data must "
                "be a dictionary."
            )

        payload = dict(data)

        industry = self._extract_industry(
            payload
        )

        if not industry:
            raise ValueError(
                "Industry processing requires "
                "a canonical industry classification."
            )

        payload["industry"] = industry

        result = await self.processing_pipeline.process(
            payload
        )

        if not isinstance(
            result,
            dict,
        ):
            raise TypeError(
                "IndustryProcessingPipeline must "
                "return a dictionary."
            )

        processed_industry = self._extract_industry(
            result
        )

        if not processed_industry:
            raise ValueError(
                "IndustryProcessingPipeline returned "
                "no canonical industry."
            )

        result = dict(result)

        result["industry"] = processed_industry

        return result

    # ==================================================================
    # CANONICAL IDENTIFIER GENERATION
    # ==================================================================

    @classmethod
    def _ensure_canonical_identifiers(
        cls,
        data: dict[str, Any],
        *,
        preserve_existing_code: bool = False,
    ) -> dict[str, Any]:
        """
        Ensure the Industry persistence payload contains valid
        canonical identifiers.

        Database invariant:

            industries.code IS NOT NULL

        Provider invariant:

            industry may be supplied without code.

        Therefore:

            industry = "Software - Application"

        becomes:

            name = "Software - Application"
            code = "software_application"
            slug = "software-application"

        Real classification codes are preserved when supplied.
        """

        payload = dict(data)

        industry = cls._extract_industry(
            payload
        )

        if not industry:
            raise ValueError(
                "Cannot generate canonical identifiers "
                "without an industry name."
            )

        payload["industry"] = industry

        existing_code = cls._clean_string(
            payload.get("code")
        )

        # --------------------------------------------------------------
        # Prefer an actual classification code when available.
        # --------------------------------------------------------------

        if not existing_code:

            for key in (
                "gics_code",
                "naics_code",
                "sic_code",
                "icb_code",
                "industry_code",
                "classification_code",
            ):
                candidate = cls._clean_string(
                    payload.get(key)
                )

                if candidate:
                    existing_code = candidate
                    break

        # --------------------------------------------------------------
        # Deterministic fallback.
        # --------------------------------------------------------------

        if not existing_code:

            existing_code = cls._generate_canonical_code(
                industry
            )

        payload["code"] = existing_code

        # --------------------------------------------------------------
        # Slug is useful for stable API/UI references.
        # --------------------------------------------------------------

        existing_slug = cls._clean_string(
            payload.get("slug")
        )

        if not existing_slug:
            payload["slug"] = cls._generate_slug(
                industry
            )

        return payload

    # ==================================================================
    # CANONICAL CODE
    # ==================================================================

    @classmethod
    def _generate_canonical_code(
        cls,
        industry: str,
    ) -> str:
        """
        Generate a deterministic internal canonical industry code.

        Examples:

            Software - Application
                ->
            software_application

            Semiconductors
                ->
            semiconductors

            Oil & Gas Exploration
                ->
            oil_gas_exploration
        """

        normalized = unicodedata.normalize(
            "NFKD",
            industry,
        )

        normalized = normalized.encode(
            "ascii",
            "ignore",
        ).decode(
            "ascii"
        )

        normalized = normalized.lower()

        normalized = re.sub(
            r"[^a-z0-9]+",
            "_",
            normalized,
        )

        normalized = re.sub(
            r"_+",
            "_",
            normalized,
        )

        normalized = normalized.strip(
            "_"
        )

        if not normalized:
            raise ValueError(
                "Unable to generate a canonical "
                "industry code from industry name."
            )

        return normalized

    # ==================================================================
    # SLUG
    # ==================================================================

    @classmethod
    def _generate_slug(
        cls,
        industry: str,
    ) -> str:
        """
        Generate a URL/API-safe industry slug.
        """

        normalized = unicodedata.normalize(
            "NFKD",
            industry,
        )

        normalized = normalized.encode(
            "ascii",
            "ignore",
        ).decode(
            "ascii"
        )

        normalized = normalized.lower()

        normalized = re.sub(
            r"[^a-z0-9]+",
            "-",
            normalized,
        )

        normalized = re.sub(
            r"-+",
            "-",
            normalized,
        )

        return normalized.strip("-")

    # ==================================================================
    # INDUSTRY EXTRACTION
    # ==================================================================

    @classmethod
    def _extract_industry(
        cls,
        data: dict[str, Any],
    ) -> str | None:

        if not isinstance(
            data,
            dict,
        ):
            return None

        for key in (
            "industry",
            "industry_name",
            "canonical_industry",
            "classification",
            "classification_name",
            "name",
        ):

            value = cls._clean_string(
                data.get(key)
            )

            if value:
                return value

        return None

    # ==================================================================
    # STRING CLEANING
    # ==================================================================

    @staticmethod
    def _clean_string(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            value = str(value)

        value = value.strip()

        return value or None

    # ==================================================================
    # TICKER NORMALIZATION
    # ==================================================================

    @classmethod
    def _normalize_ticker(
        cls,
        value: Any,
    ) -> str | None:

        value = cls._clean_string(
            value
        )

        if not value:
            return None

        return value.upper()