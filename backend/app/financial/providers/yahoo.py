"""
app/financial/providers/yahoo.py

Yahoo Finance financial-data provider.

This provider is exposed through the application's ToolRouter.

Architecture:

    ToolRouter
        |
        v
    YahooFinancialTool
        |
        v
    yfinance
        |
        v
    Normalized financial data

The provider does not perform financial analysis.
It only acquires financial information.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import yfinance as yf

from app.tools.base.base_tool import BaseTool

logger = logging.getLogger(__name__)


class YahooFinancialTool(BaseTool):
    """
    Retrieve core financial data from Yahoo Finance.

    Provides:

    - company information
    - income statement
    - balance sheet
    - cash flow statement
    - basic financial metrics
    - source metadata
    """

    name = "financial.yahoo"

    description = (
        "Retrieve core company financial data from Yahoo Finance."
    )

    async def execute(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:

        symbol = (
            ticker
            or company
        )

        if not symbol:
            return {
                "success": False,
                "output": None,
                "error": (
                    "ticker or company is required"
                ),
            }

        logger.info(
            "Yahoo financial tool started | "
            "company=%r | ticker=%r",
            company,
            ticker,
        )

        try:

            data = await asyncio.to_thread(
                self._fetch,
                symbol,
            )

            return {
                "success": True,
                "output": data,
                "error": None,
            }

        except Exception as exc:

            logger.exception(
                "Yahoo financial retrieval failed | "
                "symbol=%r",
                symbol,
            )

            return {
                "success": False,
                "output": None,
                "error": str(exc),
            }

    # =====================================================
    # Synchronous Yahoo retrieval
    # =====================================================

    def _fetch(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        ticker = yf.Ticker(symbol)

        info = self._safe_info(
            ticker
        )

        income_statement = (
            self._statement_to_dict(
                ticker.income_stmt
            )
        )

        balance_sheet = (
            self._statement_to_dict(
                ticker.balance_sheet
            )
        )

        cash_flow_statement = (
            self._statement_to_dict(
                ticker.cashflow
            )
        )

        financial_metrics = {
            "market_cap": info.get(
                "marketCap"
            ),
            "enterprise_value": info.get(
                "enterpriseValue"
            ),
            "trailing_pe": info.get(
                "trailingPE"
            ),
            "forward_pe": info.get(
                "forwardPE"
            ),
            "price_to_book": info.get(
                "priceToBook"
            ),
            "price_to_sales": info.get(
                "priceToSalesTrailing12Months"
            ),
            "profit_margin": info.get(
                "profitMargins"
            ),
            "operating_margin": info.get(
                "operatingMargins"
            ),
            "return_on_equity": info.get(
                "returnOnEquity"
            ),
            "return_on_assets": info.get(
                "returnOnAssets"
            ),
            "revenue_growth": info.get(
                "revenueGrowth"
            ),
            "earnings_growth": info.get(
                "earningsGrowth"
            ),
            "debt_to_equity": info.get(
                "debtToEquity"
            ),
            "current_ratio": info.get(
                "currentRatio"
            ),
            "quick_ratio": info.get(
                "quickRatio"
            ),
            "free_cash_flow": info.get(
                "freeCashflow"
            ),
            "operating_cash_flow": info.get(
                "operatingCashflow"
            ),
        }

        company_name = (
            info.get("longName")
            or info.get("shortName")
            or symbol
        )

        resolved_ticker = (
            info.get("symbol")
            or symbol
        )

        return {
            "company": company_name,
            "company_name": company_name,
            "ticker": resolved_ticker,
            "industry": info.get(
                "industry"
            ),
            "sector": info.get(
                "sector"
            ),
            "country": info.get(
                "country"
            ),
            "exchange": info.get(
                "exchange"
            ),
            "currency": info.get(
                "currency"
            ),
            "website": info.get(
                "website"
            ),
            "description": info.get(
                "longBusinessSummary"
            ),
            "employees": info.get(
                "fullTimeEmployees"
            ),
            "headquarters": {
                "address1": info.get(
                    "address1"
                ),
                "city": info.get(
                    "city"
                ),
                "state": info.get(
                    "state"
                ),
                "country": info.get(
                    "country"
                ),
            },
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow_statement": cash_flow_statement,
            "financial_metrics": financial_metrics,
            "sources": [
                {
                    "provider": "Yahoo Finance",
                    "type": "financial_data",
                    "ticker": resolved_ticker,
                }
            ],
        }

    # =====================================================
    # Yahoo helpers
    # =====================================================

    @staticmethod
    def _safe_info(
        ticker: yf.Ticker,
    ) -> dict[str, Any]:

        try:

            info = ticker.info

            if isinstance(
                info,
                dict,
            ):
                return info

        except Exception:

            logger.exception(
                "Yahoo info retrieval failed"
            )

        return {}

    @staticmethod
    def _statement_to_dict(
        statement: Any,
    ) -> dict[str, Any]:

        if statement is None:
            return {}

        try:

            if hasattr(
                statement,
                "to_dict",
            ):

                raw = statement.to_dict()

                return YahooFinancialTool._json_safe(
                    raw
                )

        except Exception:

            logger.exception(
                "Failed to serialize Yahoo statement"
            )

        return {}

    @staticmethod
    def _json_safe(
        value: Any,
    ) -> Any:

        if value is None:
            return None

        if isinstance(
            value,
            dict,
        ):

            return {
                str(key): YahooFinancialTool._json_safe(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (
                list,
                tuple,
                set,
            ),
        ):

            return [
                YahooFinancialTool._json_safe(
                    item
                )
                for item in value
            ]

        if hasattr(
            value,
            "item",
        ):

            try:
                return value.item()
            except Exception:
                pass

        return value