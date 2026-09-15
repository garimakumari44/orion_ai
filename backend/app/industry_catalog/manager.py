"""
app/industry_catalog/manager.py

Industry Catalog Manager.

Application-facing entry point for industry resolution.
"""

from __future__ import annotations

from typing import Any

from   .models   import IndustryResult
from .resolver import IndustryResolver


class IndustryCatalogManager:
    """
    Application-level manager for canonical industry resolution.

    The manager coordinates the resolver but does not contain
    classification logic itself.
    """

    def __init__(
        self,
        resolver: IndustryResolver | None = None,
    ) -> None:
        self.resolver = resolver or IndustryResolver()

    def resolve(
        self,
        *,
        company_record: Any | None = None,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        company_id: int | None = None,
    ) -> IndustryResult:
        """
        Resolve canonical industry.
        """

        return self.resolver.resolve(
            company_record=company_record,
            company=company,
            ticker=ticker,
            industry=industry,
            company_id=company_id,
        )

    def resolve_from_company(
        self,
        company_record: Any,
    ) -> IndustryResult:
        """
        Resolve industry directly from a Company record.
        """

        return self.resolve(
            company_record=company_record,
        )