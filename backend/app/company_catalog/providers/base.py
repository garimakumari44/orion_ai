"""
app/company_catalog/providers/base.py

Canonical interface for company-data providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Canonical interface for external company-data providers.
    """

    # ------------------------------------------------------------------
    # Provider Identity
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Stable provider identifier.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    @abstractmethod
    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search for companies.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    @abstractmethod
    async def list_companies(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Return a batch of companies.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve a company profile.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check provider availability.
        """
        raise NotImplementedError


__all__ = [
    "BaseProvider",
]