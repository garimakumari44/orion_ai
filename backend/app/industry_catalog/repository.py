"""
app/industry_catalog/repository.py

Abstract repository contract for the Industry Catalog.

This module defines the persistence interface used by the
Industry Catalog service.

Concrete implementations should live separately, for example:

    app/industry_catalog/sqlalchemy_repository.py

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
    PostgreSQL
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IndustryRepository(ABC):
    """
    Abstract repository for industry catalog records.

    This class defines the persistence contract for the
    Industry Catalog.

    It must NOT be instantiated directly.

    Concrete implementations should inherit from this class
    and implement every abstract method.
    """

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    @abstractmethod
    async def create(
        self,
        data: dict[str, Any],
    ) -> Any:
        """
        Create a new industry catalog record.

        Parameters
        ----------
        data:
            Industry record data.

        Returns
        -------
        Any
            The newly created industry record.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_by_id(
        self,
        industry_id: int,
    ) -> Any | None:
        """
        Retrieve an industry by its database ID.

        Parameters
        ----------
        industry_id:
            Database primary key.

        Returns
        -------
        Any | None
            Industry record if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_code(
        self,
        code: str,
    ) -> Any | None:
        """
        Retrieve an industry by classification code.

        Examples of codes include:

        - SIC
        - NAICS
        - GICS
        - Internal catalog codes

        Parameters
        ----------
        code:
            Industry classification code.

        Returns
        -------
        Any | None
            Industry record if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_industry(
        self,
        industry: str,
    ) -> Any | None:
        """
        Retrieve an industry by its normalized industry name.

        Parameters
        ----------
        industry:
            Industry name.

        Returns
        -------
        Any | None
            Industry record if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_all(
        self,
    ) -> list[Any]:
        """
        Return all industry catalog records.

        Returns
        -------
        list[Any]
            List of industry records.
        """
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        query: str,
    ) -> list[Any]:
        """
        Search industry catalog records.

        Parameters
        ----------
        query:
            Search text.

        Returns
        -------
        list[Any]
            Matching industry records.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    @abstractmethod
    async def update(
        self,
        industry_id: int,
        data: dict[str, Any],
    ) -> Any | None:
        """
        Update an existing industry catalog record.

        Parameters
        ----------
        industry_id:
            Database primary key.

        data:
            Fields to update.

        Returns
        -------
        Any | None
            Updated record if found, otherwise None.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    @abstractmethod
    async def delete(
        self,
        industry_id: int,
    ) -> bool:
        """
        Delete an industry catalog record.

        Parameters
        ----------
        industry_id:
            Database primary key.

        Returns
        -------
        bool
            True if the record was deleted,
            False if it did not exist.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # UPSERT
    # ------------------------------------------------------------------

    @abstractmethod
    async def upsert(
        self,
        data: dict[str, Any],
    ) -> Any:
        """
        Create or update an industry catalog record.

        The concrete implementation decides which fields
        constitute the natural identity of an industry.

        Typical identity candidates include:

        - classification code
        - industry name
        - provider + provider code

        Parameters
        ----------
        data:
            Industry record data.

        Returns
        -------
        Any
            Created or updated industry record.
        """
        raise NotImplementedError