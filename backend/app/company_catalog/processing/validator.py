
"""
app/company_catalog/processing/validator.py

Company Validator

Validates normalized company data before deduplication,
merging, and confidence calculation.

IMPORTANT:

    sector != industry

A sector value must NEVER satisfy industry validation.

The validator intentionally requires:

    company name
    AND
    industry OR sub_industry

Ticker remains optional because private companies and
other non-public entities may not have a ticker.
"""

from __future__ import annotations

import re
from typing import Any


class CompanyValidator:
    """
    Validate normalized company dictionaries.

    This class is completely independent of SQLAlchemy,
    repositories, sessions, and external providers.
    """

    TICKER_REGEX = re.compile(
        r"^[A-Z0-9.\-]{1,10}$"
    )

    # =========================================================
    # Main Validation
    # =========================================================

    @classmethod
    def validate(
        cls,
        data: dict[str, Any],
    ) -> None:
        """
        Validate a complete normalized company record.

        Required:
            - company name
            - industry OR sub_industry

        Optional:
            - ticker
        """

        if not isinstance(data, dict):
            raise TypeError(
                "CompanyValidator.validate() requires "
                "a dictionary."
            )

        # -----------------------------------------------------
        # Company name
        # -----------------------------------------------------

        cls.validate_name(
            data.get("name")
            or data.get("company_name")
            or data.get("company")
        )

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        cls.validate_ticker(
            data.get("ticker")
            or data.get("symbol")
            or data.get("stock_symbol")
        )

        # -----------------------------------------------------
        # Industry metadata
        # -----------------------------------------------------

        cls.validate_industry(
            data.get("industry"),
            data.get("sub_industry"),
        )

    # =========================================================
    # Name Validation
    # =========================================================

    @staticmethod
    def validate_name(
        name: str | None,
    ) -> None:
        """
        Validate company name.
        """

        if name is None:
            raise ValueError(
                "Company name is required."
            )

        if not isinstance(name, str):
            raise ValueError(
                "Company name must be a string."
            )

        if not name.strip():
            raise ValueError(
                "Company name is required."
            )

    # =========================================================
    # Ticker Validation
    # =========================================================

    @classmethod
    def validate_ticker(
        cls,
        ticker: str | None,
    ) -> None:
        """
        Validate an optional stock ticker.

        Ticker is optional because some companies may not
        have a public stock symbol.
        """

        if ticker is None:
            return

        if not isinstance(ticker, str):
            raise ValueError(
                "Ticker must be a string."
            )

        ticker = ticker.strip().upper()

        # Empty ticker is treated as missing because ticker
        # is optional.
        if not ticker:
            return

        if not cls.TICKER_REGEX.fullmatch(ticker):
            raise ValueError(
                f"Invalid ticker: {ticker}"
            )

    # =========================================================
    # Industry Validation
    # =========================================================

    @staticmethod
    def validate_industry(
        industry: Any,
        sub_industry: Any,
    ) -> None:
        """
        Validate company classification metadata.

        At least one of:

            industry
            sub_industry

        must be available.

        A sub_industry without an industry is allowed because
        some providers expose granular classification without
        the parent industry.

        IMPORTANT:

            sector is intentionally NOT accepted.

        Therefore:

            sector="Technology"
            industry=None
            sub_industry=None

        is invalid.

        But:

            sector="Technology"
            industry="Software"

        is valid.

        And:

            sector="Technology"
            sub_industry="Application Software"

        is also valid.
        """

        valid_industry = (
            isinstance(industry, str)
            and bool(industry.strip())
        )

        valid_sub_industry = (
            isinstance(sub_industry, str)
            and bool(sub_industry.strip())
        )

        if not valid_industry and not valid_sub_industry:
            raise ValueError(
                "Company industry metadata is required. "
                "Provide industry or sub_industry."
            )

