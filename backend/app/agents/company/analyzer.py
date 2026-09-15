
"""
app/agents/company/analyzer.py

Coordinates all company-domain analyzers.

Responsibility:
    - Accept enriched/researched company data.
    - Run each domain-specific analyzer.
    - Aggregate the resulting analysis.

This class does NOT perform external research or retrieval.

Research/discovery should happen before this layer and populate
the company_data payload with factual company information.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from .business_model import BusinessModelAnalyzer
from .geography import GeographyAnalyzer
from .management import ManagementAnalyzer
from .ownership import OwnershipAnalyzer
from .products import ProductAnalyzer
from .profile import CompanyProfileAnalyzer
from .segments import SegmentAnalyzer

logger = logging.getLogger(__name__)


class CompanyAnalyzer:
    """
    Coordinates all company-domain analyzers.

    Expected flow:

        Research / Retrieval
                ↓
        Enriched Company Data
                ↓
        CompanyAnalyzer
                ↓
        Domain-specific analyzers
                ↓
        Company Analysis
    """

    def __init__(self) -> None:
        """
        Initialize all company-domain analyzers.
        """

        self.profile = CompanyProfileAnalyzer()
        self.business = BusinessModelAnalyzer()
        self.management = ManagementAnalyzer()
        self.ownership = OwnershipAnalyzer()
        self.products = ProductAnalyzer()
        self.geography = GeographyAnalyzer()
        self.segments = SegmentAnalyzer()

        self._analyzers = {
            "profile": self.profile,
            "business_model": self.business,
            "management": self.management,
            "ownership": self.ownership,
            "products": self.products,
            "geography": self.geography,
            "segments": self.segments,
        }

    # =========================================================
    # Public Analysis API
    # =========================================================

    def analyze(
        self,
        company_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run all company-domain analyzers against enriched
        company data.

        Important:
            This method does NOT retrieve company information.

        The caller is responsible for providing researched data,
        for example:

            {
                "company": "Apple Inc.",
                "ticker": "AAPL",
                "industry": "Technology",

                "headquarters": "Cupertino, California",
                "employees": 164000,
                "ceo": "Tim Cook",

                "executives": [...],
                "major_shareholders": [...],
                "products": [...],
                "business_segments": [...],
                "operating_regions": [...],
            }

        The individual analyzers then interpret those facts.
        """

        self._validate_company_data(company_data)

        company = company_data.get("company")
        ticker = company_data.get("ticker")

        logger.info(
            "Starting company domain analysis | "
            "company=%r | ticker=%r",
            company,
            ticker,
        )

        results: Dict[str, Any] = {}

        for name, analyzer in self._analyzers.items():

            logger.debug(
                "Running company domain analyzer | "
                "analyzer=%s | company=%r | ticker=%r",
                name,
                company,
                ticker,
            )

            try:
                result = analyzer.analyze(company_data)

                results[name] = result

                logger.debug(
                    "Company domain analyzer completed | "
                    "analyzer=%s | company=%r",
                    name,
                    company,
                )

            except Exception as exc:

                logger.exception(
                    "Company domain analyzer failed | "
                    "analyzer=%s | company=%r | ticker=%r",
                    name,
                    company,
                    ticker,
                )

                raise RuntimeError(
                    f"Company analyzer '{name}' failed: {exc}"
                ) from exc

        results["status"] = "completed"

        logger.info(
            "Company domain analysis completed | "
            "company=%r | ticker=%r | analyzers=%s",
            company,
            ticker,
            list(self._analyzers.keys()),
        )

        return results

    # =========================================================
    # Validation
    # =========================================================

    @staticmethod
    def _validate_company_data(
        company_data: Dict[str, Any],
    ) -> None:
        """
        Validate the minimum company identity required
        by the analysis layer.

        This layer requires company identity, but does not
        require every research field to be present.

        Missing factual fields should be handled by the
        research/retrieval layer rather than fabricated here.
        """

        if not isinstance(company_data, dict):
            raise TypeError(
                "company_data must be a dictionary"
            )

        if not company_data:
            raise ValueError(
                "Company data is required"
            )

        company = company_data.get("company")
        ticker = company_data.get("ticker")

        if not company and not ticker:
            raise ValueError(
                "Company data must contain either "
                "'company' or 'ticker'"
            )

