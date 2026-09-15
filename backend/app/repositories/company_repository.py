from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.company_catalog.processing.normalizer import (
    CompanyNormalizer,
)
from app.db.models.company import Company


class CompanyRepository:
    """
    Request-scoped repository for Company persistence and lookup.

    Responsibilities
    ----------------
    - Search companies.
    - Retrieve companies by ID.
    - Find duplicate candidates.
    - Create companies.
    - Update companies.
    - Upsert companies.

    The repository owns database access only.

    It does NOT:
    - create sessions
    - call external providers
    - run research
    - execute agents
    - perform planning
    """

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:

        if db is None:
            raise ValueError(
                "AsyncSession is required."
            )

        self.db = db

    # =========================================================
    # SEARCH
    # =========================================================

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Company]:
        """
        Search companies using:

        - name
        - legal_name
        - ticker
        - search_aliases

        Search is case-insensitive.
        """

        query = (query or "").strip()

        if not query:
            return []

        limit = max(
            1,
            min(int(limit), 100),
        )

        offset = max(
            0,
            int(offset),
        )

        search_term = f"%{query}%"

        conditions = []

        # -----------------------------------------------------
        # Name
        # -----------------------------------------------------

        if self._has_column("name"):
            conditions.append(
                Company.name.ilike(search_term)
            )

        # -----------------------------------------------------
        # Legal name
        # -----------------------------------------------------

        if self._has_column("legal_name"):
            conditions.append(
                Company.legal_name.ilike(search_term)
            )

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        if self._has_column("ticker"):
            conditions.append(
                Company.ticker.ilike(search_term)
            )

        # -----------------------------------------------------
        # Search aliases
        # -----------------------------------------------------

        if self._has_column("search_aliases"):
            conditions.append(
                Company.search_aliases.ilike(
                    search_term
                )
            )

        # No searchable fields.
        if not conditions:
            return []

        statement = select(Company)

        if self._has_column("is_active"):
            statement = statement.where(
                Company.is_active.is_(True)
            )

        statement = (
            statement
            .where(or_(*conditions))
            .order_by(
                Company.name.asc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    # =========================================================
    # GET
    # =========================================================

    async def get_by_id(
        self,
        company_id: int,
    ) -> Company | None:

        statement = select(Company).where(
            Company.id == company_id
        )

        if self._has_column("is_active"):
            statement = statement.where(
                Company.is_active.is_(True)
            )

        result = await self.db.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_by_id_any(
        self,
        company_id: int,
    ) -> Company | None:

        result = await self.db.execute(
            select(Company).where(
                Company.id == company_id
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # FIND CANDIDATES
    # =========================================================

    async def find_candidates(
        self,
        company: dict[str, Any],
    ) -> list[Company]:
        """
        Find possible existing company records.

        Priority:

        1. CIK
        2. LEI
        3. FIGI
        4. ISIN
        5. ticker + exchange
        6. ticker
        7. normalized name
        8. name/legal_name
        """

        if not isinstance(company, dict):
            raise TypeError(
                "company must be a dictionary."
            )

        normalized = CompanyNormalizer.normalize(
            company
        )

        active = self._active_condition()

        # -----------------------------------------------------
        # Strong identifiers
        # -----------------------------------------------------

        for field in (
            "cik",
            "lei",
            "figi",
            "isin",
        ):

            if not self._has_column(field):
                continue

            value = normalized.get(field)

            if not self._has_value(value):
                continue

            value = self._normalize_identifier(
                field,
                value,
            )

            statement = (
                select(Company)
                .where(
                    active,
                    getattr(Company, field) == value,
                )
                .limit(20)
            )

            result = await self.db.execute(
                statement
            )

            candidates = list(
                result.scalars().all()
            )

            if candidates:
                return candidates

        # -----------------------------------------------------
        # Ticker + Exchange
        # -----------------------------------------------------

        ticker = normalized.get("ticker")
        exchange = normalized.get("exchange")

        if (
            self._has_column("ticker")
            and self._has_value(ticker)
            and self._has_column("exchange")
            and self._has_value(exchange)
        ):

            statement = (
                select(Company)
                .where(
                    active,
                    Company.ticker
                    == str(ticker).strip().upper(),
                    Company.exchange
                    == str(exchange).strip(),
                )
                .limit(20)
            )

            result = await self.db.execute(
                statement
            )

            candidates = list(
                result.scalars().all()
            )

            if candidates:
                return candidates

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        if (
            self._has_column("ticker")
            and self._has_value(ticker)
        ):

            statement = (
                select(Company)
                .where(
                    active,
                    Company.ticker
                    == str(ticker).strip().upper(),
                )
                .limit(20)
            )

            result = await self.db.execute(
                statement
            )

            candidates = list(
                result.scalars().all()
            )

            if candidates:
                return candidates

        # -----------------------------------------------------
        # Normalized name
        # -----------------------------------------------------

        normalized_name = normalized.get(
            "normalized_name"
        )

        if (
            self._has_column("normalized_name")
            and self._has_value(normalized_name)
        ):

            statement = (
                select(Company)
                .where(
                    active,
                    Company.normalized_name
                    == str(
                        normalized_name
                    ).strip().lower(),
                )
                .limit(20)
            )

            result = await self.db.execute(
                statement
            )

            candidates = list(
                result.scalars().all()
            )

            if candidates:
                return candidates

        # -----------------------------------------------------
        # Name / Legal Name
        # -----------------------------------------------------

        name = normalized.get("name")
        legal_name = normalized.get("legal_name")

        conditions = []

        if (
            self._has_column("name")
            and self._has_value(name)
        ):
            conditions.append(
                Company.name.ilike(
                    f"%{str(name).strip()}%"
                )
            )

        if (
            self._has_column("legal_name")
            and self._has_value(name)
        ):
            conditions.append(
                Company.legal_name.ilike(
                    f"%{str(name).strip()}%"
                )
            )

        if (
            self._has_column("name")
            and self._has_value(legal_name)
        ):
            conditions.append(
                Company.name.ilike(
                    f"%{str(legal_name).strip()}%"
                )
            )

        if (
            self._has_column("legal_name")
            and self._has_value(legal_name)
        ):
            conditions.append(
                Company.legal_name.ilike(
                    f"%{str(legal_name).strip()}%"
                )
            )

        if not conditions:
            return []

        statement = (
            select(Company)
            .where(
                active,
                or_(*conditions),
            )
            .order_by(
                Company.name.asc()
            )
            .limit(20)
        )

        result = await self.db.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    # =========================================================
    # UPSERT
    # =========================================================

    async def upsert(
        self,
        company_data: dict[str, Any],
    ) -> Company:

        if not company_data:
            raise ValueError(
                "company_data is required."
            )

        normalized = self._normalize_company_data(
            company_data
        )

        clean = self._clean_company_data(
            normalized
        )

        if not clean:
            raise ValueError(
                "No valid Company fields were provided."
            )

        candidates = await self.find_candidates(
            normalized
        )

        if candidates:

            company = candidates[0]

            self._merge_into_model(
                company,
                clean,
            )

        else:

            # name is required by the database.
            name = clean.get("name")

            if not self._has_value(name):
                raise ValueError(
                    "Company name is required."
                )

            company = Company(
                **clean
            )

            self.db.add(company)

        await self.db.commit()

        await self.db.refresh(
            company
        )

        return company

    # =========================================================
    # CREATE
    # =========================================================

    async def create(
        self,
        company_data: dict[str, Any],
    ) -> Company:

        if not company_data:
            raise ValueError(
                "company_data is required."
            )

        normalized = self._normalize_company_data(
            company_data
        )

        clean = self._clean_company_data(
            normalized
        )

        if not clean:
            raise ValueError(
                "No valid Company fields were provided."
            )

        if not self._has_value(
            clean.get("name")
        ):
            raise ValueError(
                "Company name is required."
            )

        company = Company(
            **clean
        )

        self.db.add(company)

        await self.db.commit()

        await self.db.refresh(
            company
        )

        return company

    # =========================================================
    # UPDATE
    # =========================================================

    async def update(
        self,
        company_id: int,
        company_data: dict[str, Any],
    ) -> Company | None:

        company = await self.get_by_id(
            company_id
        )

        if company is None:
            return None

        normalized = self._normalize_company_data(
            company_data
        )

        clean = self._clean_company_data(
            normalized
        )

        self._merge_into_model(
            company,
            clean,
        )

        await self.db.commit()

        await self.db.refresh(
            company
        )

        return company

    # =========================================================
    # DATA CLEANING
    # =========================================================

    @classmethod
    def _clean_company_data(
        cls,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        valid_columns = {
            column.name
            for column in Company.__table__.columns
        }

        return {
            key: value
            for key, value in data.items()
            if key in valid_columns
        }

    @staticmethod
    def _normalize_company_data(
        data: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(data, dict):
            raise TypeError(
                "company_data must be a dictionary."
            )

        normalized = CompanyNormalizer.normalize(
            data
        )

        # Ticker
        if "ticker" in normalized:
            value = normalized["ticker"]

            normalized["ticker"] = (
                str(value).strip().upper()
                if value is not None
                and str(value).strip()
                else None
            )

        # Identifiers
        for field in (
            "cik",
            "lei",
            "figi",
            "isin",
        ):

            if field not in normalized:
                continue

            value = normalized[field]

            if value is None:
                continue

            value = str(value).strip()

            if field in {
                "lei",
                "figi",
                "isin",
            }:
                value = value.upper()

            normalized[field] = value or None

        return normalized

    # =========================================================
    # MERGE
    # =========================================================

    @staticmethod
    def _merge_into_model(
        company: Company,
        incoming: dict[str, Any],
    ) -> None:

        for field, value in incoming.items():

            if not CompanyRepository._has_value(
                value
            ):
                continue

            # Never change the primary key.
            if field == "id":
                continue

            setattr(
                company,
                field,
                value,
            )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _active_condition():

        if hasattr(
            Company,
            "is_active",
        ):
            return Company.is_active.is_(True)

        return true()

    @staticmethod
    def _has_column(
        field: str,
    ) -> bool:

        return field in {
            column.name
            for column in Company.__table__.columns
        }

    @staticmethod
    def _has_value(
        value: Any,
    ) -> bool:

        if value is None:
            return False

        if isinstance(value, str):
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

    @staticmethod
    def _normalize_identifier(
        field: str,
        value: Any,
    ) -> str:

        value = str(
            value
        ).strip()

        if field in {
            "lei",
            "figi",
            "isin",
        }:
            value = value.upper()

        return value