"""
app/industry_catalog/sqlalchemy_repository.py

Concrete SQLAlchemy repository for the Industry Catalog.

Architecture:

    IndustryCatalogService
            |
            v
    IndustryRepository
            |
            v
    SQLAlchemyIndustryRepository
            |
            v
        AsyncSession
            |
            v
        PostgreSQL

The repository receives a session factory rather than a single
long-lived AsyncSession.

This keeps database sessions request/operation scoped and prevents
the application lifespan from owning a permanent database session.

IMPORTANT
---------

The application/domain layer may refer to an industry value as:

    industry

The canonical SQLAlchemy Industry model stores that value as:

    Industry.name

Therefore this repository MUST NOT use:

    Industry.industry

unless the ORM model explicitly defines such a column.

Canonical mapping:

    application "industry"
            |
            v
    ORM "Industry.name"


PERSISTENCE BOUNDARY
--------------------

The industry enrichment pipeline may return additional context such as:

    company
    ticker
    company_id
    sector
    sub_industry
    provider metadata
    classification metadata

Those values may be useful to the application/service layer, but they
must NOT automatically become Industry ORM constructor arguments.

This repository therefore:

1. Maps application "industry" -> ORM "name".
2. Removes application-only/context-only fields.
3. Keeps only fields actually mapped by the Industry ORM model.
4. Never passes arbitrary provider payload keys into Industry(...).
5. Never treats sector as industry.
6. Never stores the company name in Industry.name.
7. Guarantees that Industry.code is populated before persistence.
8. Uses a deterministic fallback code when no external classification
   code is supplied.

CANONICAL CODE
--------------

If the provider supplies a real classification code, it is preferred.

For example:

    gics_code = "451020"

becomes:

    code = "451020"

If no classification code is available, the repository generates an
internal deterministic canonical code from the industry name.

Example:

    "Software - Application"

becomes:

    code = "software_application"

This prevents PostgreSQL from receiving:

    code = NULL

when industries.code is NOT NULL.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from typing import Any

from sqlalchemy import inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.industry import Industry
from app.industry_catalog.repository import IndustryRepository


class SQLAlchemyIndustryRepository(IndustryRepository):
    """
    SQLAlchemy implementation of IndustryRepository.

    Parameters
    ----------
    session_factory:
        Callable that creates an AsyncSession.

    Example
    -------

        repository = SQLAlchemyIndustryRepository(
            session_factory=AsyncSessionLocal,
        )
    """

    # ==================================================================
    # APPLICATION / PIPELINE FIELDS THAT MUST NEVER BE PERSISTED
    # ==================================================================

    _CONTEXT_ONLY_FIELDS = frozenset(
        {
            "company",
            "company_name",
            "company_id",
            "ticker",
            "sector",
            "sub_industry",
            "industry_source",
            "industry_record",
        }
    )

    # Application aliases for the canonical Industry.name field.
    _INDUSTRY_ALIASES = (
        "industry",
        "industry_name",
        "canonical_industry",
        "classification",
        "classification_name",
    )

    # External classification fields that may provide a real code.
    _CLASSIFICATION_CODE_FIELDS = (
        "gics_code",
        "naics_code",
        "sic_code",
        "icb_code",
        "industry_code",
        "classification_code",
    )

    # ==================================================================
    # INIT
    # ==================================================================

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ) -> None:

        if session_factory is None:
            raise ValueError(
                "session_factory is required."
            )

        self.session_factory = session_factory

    # ==================================================================
    # INTERNAL HELPERS
    # ==================================================================

    @classmethod
    def _mapped_field_names(cls) -> set[str]:
        """
        Return the actual mapped ORM attribute names for Industry.

        This prevents provider metadata from being blindly passed into:

            Industry(**payload)

        Only attributes mapped by SQLAlchemy are considered.
        """

        mapper = inspect(Industry)

        return {
            attribute.key
            for attribute in mapper.column_attrs
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _clean_string(
        value: Any,
    ) -> str | None:
        """
        Convert a value to a normalized non-empty string.
        """

        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            value = str(value)

        value = value.strip()

        return value or None

    # ------------------------------------------------------------------

    @classmethod
    def _normalize_code(
        cls,
        code: Any,
    ) -> str | None:
        """
        Normalize a classification/canonical code.
        """

        code = cls._clean_string(code)

        if not code:
            return None

        return code

    # ------------------------------------------------------------------

    @classmethod
    def _generate_fallback_code(
        cls,
        industry_name: str,
    ) -> str:
        """
        Generate a deterministic internal canonical industry code.

        Examples
        --------

            Software - Application
                ->
            software_application

            Semiconductors
                ->
            semiconductors

            Oil & Gas Exploration
                ->
            oil_gas_exploration

        This is NOT intended to replace a real GICS/NAICS/SIC/ICB
        classification code when one is available.

        It is an internal canonical identifier used to satisfy the
        Industry.code database invariant.
        """

        normalized = unicodedata.normalize(
            "NFKD",
            industry_name,
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
                "Unable to generate a canonical industry "
                "code from the supplied industry name."
            )

        return normalized

    # ------------------------------------------------------------------

    @classmethod
    def _generate_slug(
        cls,
        industry_name: str,
    ) -> str:
        """
        Generate a deterministic URL/API-safe slug.

        Example:

            Software - Application
                ->
            software-application
        """

        normalized = unicodedata.normalize(
            "NFKD",
            industry_name,
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

    # ------------------------------------------------------------------

    @classmethod
    def _extract_industry_name(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Extract the canonical industry name from application/provider
        data.

        Priority:

            name
            industry
            industry_name
            canonical_industry
            classification
            classification_name
        """

        candidates = (
            data.get("name"),
            data.get("industry"),
            data.get("industry_name"),
            data.get("canonical_industry"),
            data.get("classification"),
            data.get("classification_name"),
        )

        for value in candidates:

            value = cls._clean_string(
                value
            )

            if value:
                return value

        return None

    # ------------------------------------------------------------------

    @classmethod
    def _extract_code(
        cls,
        data: dict[str, Any],
    ) -> str | None:
        """
        Extract the best available code.

        Priority:

            1. Explicit canonical code
            2. GICS
            3. NAICS
            4. SIC
            5. ICB
            6. industry_code
            7. classification_code
        """

        # Explicit canonical code first.
        code = cls._normalize_code(
            data.get("code")
        )

        if code:
            return code

        # Then look for external classification codes.
        for field in cls._CLASSIFICATION_CODE_FIELDS:

            code = cls._normalize_code(
                data.get(field)
            )

            if code:
                return code

        return None

    # ------------------------------------------------------------------

    @classmethod
    def _normalize_data(
        cls,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize application/provider data into valid Industry ORM data.

        Example input:

            {
                "industry": "Software - Application",
                "company": "8X8 INC /DE/",
                "ticker": "EGHT",
                "company_id": 243,
                "sector": "Information Technology",
            }

        Possible normalized result:

            {
                "name": "Software - Application",
                "code": "software_application",
                "slug": "software-application",
            }

        If an actual classification code is supplied:

            {
                "industry": "Software - Application",
                "gics_code": "451020",
            }

        the result will contain:

            {
                "name": "Software - Application",
                "code": "451020",
                "gics_code": "451020",
            }

        IMPORTANT:

        "industry" is an application-level alias.

        "name" is the canonical ORM field.

        Therefore:

            industry -> name

        and never:

            industry -> Industry.industry
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Industry repository data must be a dictionary."
            )

        source = dict(data)

        # --------------------------------------------------------------
        # Determine canonical Industry.name
        # --------------------------------------------------------------

        industry_name = cls._extract_industry_name(
            source
        )

        # --------------------------------------------------------------
        # Get actual ORM mapped fields
        # --------------------------------------------------------------

        mapped_fields = cls._mapped_field_names()

        normalized: dict[str, Any] = {}

        # --------------------------------------------------------------
        # Canonical industry name
        # --------------------------------------------------------------

        if industry_name:

            if "name" not in mapped_fields:
                raise RuntimeError(
                    "Industry ORM model does not define the required "
                    "canonical 'name' column."
                )

            normalized["name"] = industry_name

        # --------------------------------------------------------------
        # Canonical code
        # --------------------------------------------------------------
        #
        # This is the important fix for:
        #
        # asyncpg.exceptions.NotNullViolationError:
        # null value in column "code"
        #
        # If code is supplied, preserve it.
        #
        # Otherwise check external classification codes.
        #
        # If none exist, generate a deterministic internal code.
        # --------------------------------------------------------------

        if "code" in mapped_fields:

            code = cls._extract_code(
                source
            )

            if not code and industry_name:

                code = cls._generate_fallback_code(
                    industry_name
                )

            if not code:

                raise ValueError(
                    "Industry code is required and could not "
                    "be generated because the canonical industry "
                    "name is missing."
                )

            normalized["code"] = code

        # --------------------------------------------------------------
        # Canonical slug
        # --------------------------------------------------------------

        if "slug" in mapped_fields and industry_name:

            slug = cls._clean_string(
                source.get("slug")
            )

            if not slug:
                slug = cls._generate_slug(
                    industry_name
                )

            if slug:
                normalized["slug"] = slug

        # --------------------------------------------------------------
        # Persist only actual ORM fields.
        #
        # Context-only fields are explicitly excluded even if the ORM
        # model were ever extended with similarly named attributes.
        # --------------------------------------------------------------

        for field, value in source.items():

            # Application aliases are handled separately.
            if field in cls._INDUSTRY_ALIASES:
                continue

            # Context-only fields must never cross the persistence
            # boundary.
            if field in cls._CONTEXT_ONLY_FIELDS:
                continue

            # Never persist SQLAlchemy/internal attributes.
            if field.startswith("_"):
                continue

            # Canonical fields are already handled above.
            if field in {
                "name",
                "code",
                "slug",
            }:
                continue

            # Only actual Industry mapped columns are accepted.
            if field not in mapped_fields:
                continue

            normalized[field] = value

        return normalized

    # ==================================================================
    # CREATE
    # ==================================================================

    async def create(
        self,
        data: dict[str, Any],
    ) -> Industry:
        """
        Create a canonical Industry record.
        """

        normalized_data = self._normalize_data(
            data
        )

        if not normalized_data.get("name"):
            raise ValueError(
                "Cannot create Industry without "
                "a canonical name."
            )

        if (
            "code" in self._mapped_field_names()
            and not normalized_data.get("code")
        ):
            raise ValueError(
                "Cannot create Industry without "
                "a canonical code."
            )

        async with self.session_factory() as session:

            industry = Industry(
                **normalized_data
            )

            session.add(
                industry
            )

            await session.commit()

            await session.refresh(
                industry
            )

            return industry

    # ==================================================================
    # GET BY ID
    # ==================================================================

    async def get_by_id(
        self,
        industry_id: int,
    ) -> Industry | None:
        """
        Return an Industry by primary key.
        """

        if industry_id is None:
            return None

        async with self.session_factory() as session:

            result = await session.execute(
                select(Industry).where(
                    Industry.id == industry_id
                )
            )

            return result.scalar_one_or_none()

    # ==================================================================
    # GET BY CODE
    # ==================================================================

    async def get_by_code(
        self,
        code: str,
    ) -> Industry | None:
        """
        Return an Industry by classification/canonical code.
        """

        normalized_code = self._normalize_code(
            code
        )

        if not normalized_code:
            return None

        mapped_fields = self._mapped_field_names()

        if "code" not in mapped_fields:
            raise RuntimeError(
                "Industry ORM model does not define "
                "the required 'code' column."
            )

        async with self.session_factory() as session:

            result = await session.execute(
                select(Industry).where(
                    Industry.code
                    == normalized_code
                )
            )

            return result.scalar_one_or_none()

    # ==================================================================
    # GET BY INDUSTRY
    # ==================================================================

    async def get_by_industry(
        self,
        industry: str,
    ) -> Industry | None:
        """
        Return an Industry by canonical industry name.

        Application terminology:

            industry

        ORM terminology:

            Industry.name
        """

        normalized_industry = (
            self._extract_industry_name(
                {
                    "industry": industry,
                }
            )
        )

        if not normalized_industry:
            return None

        async with self.session_factory() as session:

            result = await session.execute(
                select(Industry).where(
                    Industry.name
                    == normalized_industry
                )
            )

            return result.scalar_one_or_none()

    # ==================================================================
    # LIST ALL
    # ==================================================================

    async def list_all(
        self,
    ) -> list[Industry]:
        """
        Return all canonical industries.
        """

        async with self.session_factory() as session:

            result = await session.execute(
                select(Industry).order_by(
                    Industry.id
                )
            )

            return list(
                result.scalars().all()
            )

    # ==================================================================
    # SEARCH
    # ==================================================================

    async def search(
        self,
        query: str,
    ) -> list[Industry]:
        """
        Search canonical industries.

        Searches against:

            Industry.name
            Industry.code

        Industry.industry is intentionally NOT used.
        """

        search_query = (
            query.strip()
            if isinstance(
                query,
                str,
            )
            else str(query).strip()
        )

        if not search_query:
            return await self.list_all()

        mapped_fields = self._mapped_field_names()

        if "name" not in mapped_fields:
            raise RuntimeError(
                "Industry ORM model does not define "
                "the required 'name' column."
            )

        if "code" not in mapped_fields:
            raise RuntimeError(
                "Industry ORM model does not define "
                "the required 'code' column."
            )

        pattern = f"%{search_query}%"

        async with self.session_factory() as session:

            result = await session.execute(
                select(Industry)
                .where(
                    or_(
                        Industry.name.ilike(
                            pattern
                        ),
                        Industry.code.ilike(
                            pattern
                        ),
                    )
                )
                .order_by(
                    Industry.id
                )
            )

            return list(
                result.scalars().all()
            )

    # ==================================================================
    # UPDATE
    # ==================================================================

    async def update(
        self,
        industry_id: int,
        data: dict[str, Any],
    ) -> Industry | None:
        """
        Update an existing Industry.

        Application-level:

            industry

        is translated to ORM-level:

            name

        Unknown/provider/context fields are ignored.

        If the update contains an industry name but no code, a
        deterministic canonical code is generated.
        """

        normalized_data = self._normalize_data(
            data
        )

        async with self.session_factory() as session:

            result = await session.execute(
                select(Industry).where(
                    Industry.id == industry_id
                )
            )

            industry = (
                result.scalar_one_or_none()
            )

            if industry is None:
                return None

            for field, value in normalized_data.items():

                setattr(
                    industry,
                    field,
                    value,
                )

            await session.commit()

            await session.refresh(
                industry
            )

            return industry

    # ==================================================================
    # DELETE
    # ==================================================================

    async def delete(
        self,
        industry_id: int,
    ) -> bool:
        """
        Delete an Industry by ID.
        """

        async with self.session_factory() as session:

            result = await session.execute(
                select(Industry).where(
                    Industry.id == industry_id
                )
            )

            industry = (
                result.scalar_one_or_none()
            )

            if industry is None:
                return False

            await session.delete(
                industry
            )

            await session.commit()

            return True

    # ==================================================================
    # UPSERT
    # ==================================================================

    async def upsert(
        self,
        data: dict[str, Any],
    ) -> Industry:
        """
        Create or update an Industry.

        Lookup priority:

            1. classification/canonical code
            2. canonical industry name

        Example application input:

            {
                "industry": "Software - Application",
                "company": "8X8 INC /DE/",
                "ticker": "EGHT",
                "company_id": 243,
                "sector": "Information Technology",
            }

        Repository persistence boundary becomes:

            {
                "name": "Software - Application",
                "code": "software_application",
                "slug": "software-application",
            }

        If the provider supplies a real classification code:

            {
                "industry": "Software - Application",
                "gics_code": "451020",
            }

        the canonical code becomes:

            "451020"

        Company/ticker/company_id/sector remain application context
        and are NOT persisted as Industry fields.
        """

        normalized_data = self._normalize_data(
            data
        )

        industry_name = normalized_data.get(
            "name"
        )

        if not industry_name:
            raise ValueError(
                "Cannot upsert Industry without "
                "a canonical industry name."
            )

        # --------------------------------------------------------------
        # Final defensive code validation
        # --------------------------------------------------------------

        mapped_fields = self._mapped_field_names()

        if "code" in mapped_fields:

            code = self._normalize_code(
                normalized_data.get("code")
            )

            if not code:

                # This should normally never happen because
                # _normalize_data() already generates it.
                #
                # Keep this guard because the repository is the final
                # persistence boundary.

                code = self._generate_fallback_code(
                    industry_name
                )

                normalized_data["code"] = code

        async with self.session_factory() as session:

            existing: Industry | None = None

            # ----------------------------------------------------------
            # 1. Lookup by classification/canonical code
            # ----------------------------------------------------------

            code = normalized_data.get(
                "code"
            )

            if code is not None:

                normalized_code = (
                    self._normalize_code(
                        code
                    )
                )

                if normalized_code:

                    result = await session.execute(
                        select(Industry).where(
                            Industry.code
                            == normalized_code
                        )
                    )

                    existing = (
                        result.scalar_one_or_none()
                    )

            # ----------------------------------------------------------
            # 2. Lookup by canonical industry name
            # ----------------------------------------------------------

            if existing is None:

                result = await session.execute(
                    select(Industry).where(
                        Industry.name
                        == industry_name
                    )
                )

                existing = (
                    result.scalar_one_or_none()
                )

            # ----------------------------------------------------------
            # 3. Create new record
            # ----------------------------------------------------------

            if existing is None:

                industry = Industry(
                    **normalized_data
                )

                session.add(
                    industry
                )

                await session.commit()

                await session.refresh(
                    industry
                )

                return industry

            # ----------------------------------------------------------
            # 4. Update existing record
            # ----------------------------------------------------------

            for field, value in normalized_data.items():

                setattr(
                    existing,
                    field,
                    value,
                )

            await session.commit()

            await session.refresh(
                existing
            )

            return existing