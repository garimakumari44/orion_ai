"""
app/industry_catalog/providers/base.py

Base interfaces for Industry Catalog providers.

Industry providers are responsible for retrieving industry identity,
classification, taxonomy, and related metadata from external or
internal data sources.

The provider layer must NOT:

- persist data
- perform database operations
- run research
- execute research agents
- contain application orchestration logic

The provider layer is responsible only for:

- acquiring provider data
- normalizing provider-level responses
- exposing provider capabilities
- reporting provider health
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IndustryProviderError(Exception):
    """Base exception for industry provider errors."""


class IndustryProviderUnavailableError(IndustryProviderError):
    """Raised when an industry provider is unavailable."""


class IndustryProvider(ABC):
    """
    Abstract contract for an Industry Catalog provider.

    Implementations may connect to:

    - industry taxonomy APIs
    - market-data providers
    - government classification systems
    - internal datasets
    - web/data enrichment providers

    Providers must remain independent from:

    - SQLAlchemy
    - repositories
    - services
    - agents
    - research orchestration
    """

    name: str = "unknown"
    priority: int = 100

    def __init__(self) -> None:
        self.enabled: bool = True

    # =====================================================================
    # Provider identity
    # =====================================================================

    @property
    def provider_name(self) -> str:
        """
        Stable provider identifier.

        Examples:

            "sec"
            "yahoo"
            "openfigi"
            "internal_taxonomy"
        """

        return str(self.name).strip()

    # =====================================================================
    # Search
    # =====================================================================

    @abstractmethod
    def search_industry(
        self,
        query: str,
        *,
        limit: int = 20,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Search for industries matching a query.

        Parameters
        ----------
        query:
            Industry name, classification, keyword, etc.

        limit:
            Maximum number of results.

        kwargs:
            Optional provider-specific context.

            The manager may pass:

                company
                ticker

            together with provider-specific parameters.

        Returns
        -------
        list[dict]
            Provider results.

        Example
        -------

            [
                {
                    "industry": "Semiconductors",
                    "sub_industry": "Semiconductor Equipment",
                    "sector": "Information Technology",
                    "code": "334413",
                    "source": "provider_name",
                }
            ]
        """

        raise NotImplementedError

    # =====================================================================
    # Industry lookup
    # =====================================================================

    @abstractmethod
    def get_industry(
        self,
        industry: str,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a specific industry.

        Parameters
        ----------
        industry:
            Industry identifier or name.

        Returns
        -------
        dict | None
            Industry metadata or None if unavailable.
        """

        raise NotImplementedError

    # =====================================================================
    # Company classification
    # =====================================================================

    def classify_company(
        self,
        company: Optional[str] = None,
        *,
        ticker: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Optionally classify a company into an industry.

        Providers that do not support company classification
        should return None.

        This method MUST NOT persist anything.
        """

        return None

    # =====================================================================
    # Taxonomy
    # =====================================================================

    def get_taxonomy(
        self,
        *,
        taxonomy: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Return taxonomy/classification data.

        Examples:

            GICS
            NAICS
            SIC
            ICB

        Providers that do not support taxonomy retrieval
        return an empty list.
        """

        return []

    # =====================================================================
    # Health
    # =====================================================================

    def health_check(self) -> bool:
        """
        Check whether the provider is currently usable.

        Providers may override this to perform:

        - connectivity checks
        - credential checks
        - endpoint checks
        - configuration validation
        """

        return bool(self.enabled)

    # =====================================================================
    # Lifecycle
    # =====================================================================

    def close(self) -> None:
        """
        Release provider-owned resources.

        Override this method when the provider owns:

        - HTTP clients
        - database connections
        - sessions
        - file handles
        """

        return None

    # =====================================================================
    # Representation
    # =====================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.provider_name!r}, "
            f"priority={self.priority}, "
            f"enabled={self.enabled}"
            f")"
        )


# Backward-compatible alias.
BaseIndustryProvider = IndustryProvider