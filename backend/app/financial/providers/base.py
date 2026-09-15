"""
app/company_catalog/providers/base.py

Base Provider Interface.

All external company-data providers must implement this
contract so ProviderManager and synchronization services
can work with providers interchangeably.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Base interface for every external company-data provider.

    Provider implementations are responsible for:
    - company discovery
    - company listing
    - company profile retrieval
    - provider health checks

    ProviderManager is responsible for orchestration.
    """

    name: str = "base"

    # =========================================================
    # Search Companies
    # =========================================================

    @abstractmethod
    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search companies by name, ticker, or keyword.
        """
        raise NotImplementedError

    # =========================================================
    # List Companies
    # =========================================================

    @abstractmethod
    async def list_companies(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Return a batch of companies from the provider.

        Used for:
        - initial catalog ingestion
        - scheduled synchronization
        - catalog refresh jobs
        """
        raise NotImplementedError

    # =========================================================
    # Company Profile
    # =========================================================

    @abstractmethod
    async def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Fetch detailed company information.
        """
        raise NotImplementedError

    # =========================================================
    # Health Check
    # =========================================================

    @abstractmethod
    async def health_check(
        self,
    ) -> bool:
        """
        Verify provider availability.
        """
        raise NotImplementedError