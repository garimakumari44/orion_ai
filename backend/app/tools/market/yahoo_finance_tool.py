"""
app/tools/market/yahoo_finance_tool.py

Yahoo Finance market-data tool.

Provides a clean application-level interface around yfinance so that
agents do not directly depend on the yfinance library.

Responsibilities
----------------
- Company information
- Current market information
- Historical prices
- Income statement
- Balance sheet
- Cash flow
- Dividends
- Stock splits
- Analyst information
- Valuation metrics

This tool contains data-access logic only.
Business/LLM analysis belongs to the agent/analyzer layer.
"""

from __future__ import annotations

import logging
import math
from datetime import date, datetime
from typing import Any, Dict

import numpy as np
import pandas as pd
import yfinance as yf

from app.tools.base.base_tool import BaseTool


logger = logging.getLogger(__name__)


class YahooFinanceTool(BaseTool):
    """
    Tool for retrieving financial and market data from Yahoo Finance.

    yfinance-specific implementation details remain isolated here.
    """

    name = "yahoo_finance"

    description = (
        "Retrieves company market data, financial statements, valuation "
        "metrics, historical prices, dividends, stock splits, and analyst "
        "information using Yahoo Finance."
    )

    def __init__(self) -> None:
        super().__init__()

    # ========================================================================
    # Internal helpers
    # ========================================================================

    @staticmethod
    def _normalize_ticker(ticker: str) -> str:
        """
        Normalize and validate a ticker symbol.
        """

        if not ticker:
            raise ValueError("Ticker symbol is required.")

        normalized = str(ticker).strip().upper()

        if not normalized:
            raise ValueError("Ticker symbol cannot be empty.")

        return normalized

    @staticmethod
    def _safe_value(value: Any) -> Any:
        """
        Convert pandas/numpy/yfinance values into JSON-safe values.

        Important:
        ----------
        JSON does not support NaN or Infinity.

        This method converts:

        - None       -> None
        - pandas.NA  -> None
        - numpy.nan  -> None
        - NaN        -> None
        - +inf       -> None
        - -inf       -> None

        It also converts numpy scalar values into their native Python
        equivalents and recursively sanitizes dictionaries, lists,
        tuples, and sets.

        Datetime/date values are converted to ISO-8601 strings.
        """

        # ------------------------------------------------------------------
        # None
        # ------------------------------------------------------------------

        if value is None:
            return None

        # ------------------------------------------------------------------
        # pandas.NA / pandas.NaT
        #
        # pd.isna() can return an array for some objects, so it must be
        # handled carefully.
        # ------------------------------------------------------------------

        try:
            if value is pd.NA or value is pd.NaT:
                return None
        except Exception:
            pass

        # ------------------------------------------------------------------
        # Dictionaries
        # ------------------------------------------------------------------

        if isinstance(value, dict):
            return {
                str(key): YahooFinanceTool._safe_value(item)
                for key, item in value.items()
            }

        # ------------------------------------------------------------------
        # Lists / tuples / sets
        # ------------------------------------------------------------------

        if isinstance(value, (list, tuple, set)):
            return [
                YahooFinanceTool._safe_value(item)
                for item in value
            ]

        # ------------------------------------------------------------------
        # datetime/date
        # ------------------------------------------------------------------

        if isinstance(value, (datetime, date)):
            try:
                return value.isoformat()
            except Exception:
                return str(value)

        # ------------------------------------------------------------------
        # numpy scalar values
        #
        # Examples:
        #   np.float64(123.4)
        #   np.int64(10)
        #   np.bool_(True)
        # ------------------------------------------------------------------

        if isinstance(value, np.generic):
            try:
                value = value.item()
            except Exception:
                pass

        # ------------------------------------------------------------------
        # After numpy conversion, check normal Python numeric values.
        #
        # bool is an int subclass, so handle it separately.
        # ------------------------------------------------------------------

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float, complex)):
            try:
                # Complex numbers are not JSON-safe.
                if isinstance(value, complex):
                    if value.imag != 0:
                        return None

                    value = value.real

                # NaN / +inf / -inf -> None
                if isinstance(value, float) and not math.isfinite(value):
                    return None

                return value

            except Exception:
                return None

        # ------------------------------------------------------------------
        # pandas scalar types that may not have been handled above.
        # ------------------------------------------------------------------

        try:
            is_missing = pd.isna(value)

            # pd.isna("abc") -> False
            # pd.isna(pd.NA) -> True
            #
            # For arrays/Series pd.isna() returns an array, which we do
            # not want to treat as a boolean.
            if isinstance(is_missing, (bool, np.bool_)):
                if bool(is_missing):
                    return None

        except Exception:
            pass

        # ------------------------------------------------------------------
        # Objects exposing .item()
        #
        # Some third-party/numpy scalar types use .item() to return their
        # native Python representation.
        # ------------------------------------------------------------------

        try:
            if hasattr(value, "item"):
                converted = value.item()

                # Avoid infinite recursion if .item() returns itself.
                if converted is not value:
                    return YahooFinanceTool._safe_value(converted)

        except Exception:
            pass

        # ------------------------------------------------------------------
        # Strings and ordinary JSON-safe values.
        # ------------------------------------------------------------------

        if isinstance(value, (str, bytes)):
            if isinstance(value, bytes):
                try:
                    return value.decode("utf-8")
                except Exception:
                    return str(value)

            return value

        # ------------------------------------------------------------------
        # Final fallback.
        #
        # Keep ordinary values where possible, but make sure objects with
        # an obvious non-finite numeric representation cannot leak through.
        # ------------------------------------------------------------------

        try:
            if isinstance(value, float) and not math.isfinite(value):
                return None
        except Exception:
            pass

        return value

    @staticmethod
    def _dataframe_to_records(data: Any) -> list[Dict[str, Any]]:
        """
        Convert a pandas DataFrame into JSON-friendly records.

        yfinance returns DataFrames with dates as indexes. This method
        converts the index into a regular field and recursively sanitizes
        all values.
        """

        if data is None:
            return []

        try:
            if not isinstance(data, pd.DataFrame):
                return []

            if data.empty:
                return []

            result = data.copy()
            result = result.reset_index()

            records = result.to_dict(orient="records")

            cleaned: list[Dict[str, Any]] = []

            for record in records:
                cleaned_record: Dict[str, Any] = {}

                for key, value in record.items():
                    cleaned_record[str(key)] = (
                        YahooFinanceTool._safe_value(value)
                    )

                cleaned.append(cleaned_record)

            return cleaned

        except Exception as exc:
            logger.exception(
                "Failed converting Yahoo Finance DataFrame to records: %s",
                exc,
            )
            return []

    @staticmethod
    def _info_to_dict(info: Any) -> Dict[str, Any]:
        """
        Safely convert ticker.info into a recursively JSON-safe dictionary.
        """

        if not isinstance(info, dict):
            return {}

        result: Dict[str, Any] = {}

        for key, value in info.items():
            result[str(key)] = YahooFinanceTool._safe_value(value)

        return result

    def _get_ticker(self, ticker: str) -> yf.Ticker:
        """
        Create a yfinance Ticker instance.
        """

        normalized = self._normalize_ticker(ticker)

        return yf.Ticker(normalized)

    # ========================================================================
    # Main execution interface
    # ========================================================================

    def execute(
        self,
        ticker: str,
        operation: str = "overview",
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Any]:
        """
        Execute a Yahoo Finance operation.

        Supported operations:

        - overview
        - info
        - price
        - history
        - income_statement
        - balance_sheet
        - cash_flow
        - financials
        - dividends
        - splits
        - analysts
        - valuation
        """

        normalized_ticker = self._normalize_ticker(ticker)

        operation = str(operation).strip().lower()

        logger.info(
            "Yahoo Finance request: ticker=%s operation=%s",
            normalized_ticker,
            operation,
        )

        try:
            ticker_obj = self._get_ticker(normalized_ticker)

            if operation == "overview":
                return self.get_overview(
                    ticker_obj,
                    requested_ticker=normalized_ticker,
                )

            if operation == "info":
                return self.get_info(
                    ticker_obj,
                    requested_ticker=normalized_ticker,
                )

            if operation in {
                "price",
                "history",
                "price_history",
            }:
                return self.get_price_history(
                    ticker_obj,
                    period=period,
                    interval=interval,
                )

            if operation in {
                "income",
                "income_statement",
                "financials_income",
            }:
                return self.get_income_statement(ticker_obj)

            if operation in {
                "balance",
                "balance_sheet",
            }:
                return self.get_balance_sheet(ticker_obj)

            if operation in {
                "cashflow",
                "cash_flow",
            }:
                return self.get_cash_flow(ticker_obj)

            if operation == "financials":
                return self.get_financials(ticker_obj)

            if operation == "dividends":
                return self.get_dividends(ticker_obj)

            if operation == "splits":
                return self.get_splits(ticker_obj)

            if operation in {
                "analysts",
                "analyst",
                "analyst_data",
            }:
                return self.get_analyst_data(ticker_obj)

            if operation == "valuation":
                return self.get_valuation(ticker_obj)

            raise ValueError(
                f"Unsupported Yahoo Finance operation: {operation}"
            )

        except Exception as exc:
            logger.exception(
                "Yahoo Finance request failed: ticker=%s operation=%s",
                normalized_ticker,
                operation,
            )

            return {
                "success": False,
                "source": "yahoo_finance",
                "ticker": normalized_ticker,
                "operation": operation,
                "error": str(exc),
            }

    # ========================================================================
    # Company overview
    # ========================================================================

    def get_overview(
        self,
        ticker_obj: yf.Ticker,
        *,
        requested_ticker: str | None = None,
    ) -> Dict[str, Any]:
        """
        Get a compact company overview.

        CONTRACT
        --------
        This method returns the canonical tool-level overview structure:

            {
                "success": True,
                "source": "yahoo_finance",
                "ticker": "AAPL",
                "company": {
                    "name": "...",
                    "symbol": "AAPL",
                    "sector": "...",
                    "industry": "...",
                    ...
                },
                "market": {...},
                "valuation": {...}
            }

        Industry providers consume `company.sector` and
        `company.industry`.
        """

        info = self._info_to_dict(ticker_obj.info)

        symbol = (
            info.get("symbol")
            or getattr(ticker_obj, "ticker", None)
            or requested_ticker
        )

        company_name = (
            info.get("longName")
            or info.get("shortName")
        )

        company = {
            "name": company_name,
            "symbol": symbol,

            "exchange": info.get("exchange"),
            "currency": info.get("currency"),

            # --------------------------------------------------------------
            # Industry classification fields
            # --------------------------------------------------------------

            "sector": info.get("sector"),
            "industry": info.get("industry"),

            # yfinance does not consistently expose a sub-industry field,
            # but preserve it if a version/data source provides one.
            "sub_industry": (
                info.get("subIndustry")
                or info.get("sub_industry")
            ),

            # --------------------------------------------------------------
            # Company metadata
            # --------------------------------------------------------------

            "country": info.get("country"),
            "website": info.get("website"),
            "city": info.get("city"),
            "state": info.get("state"),
            "zip": info.get("zip"),

            "employees": info.get("fullTimeEmployees"),
            "description": info.get("longBusinessSummary"),
        }

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": symbol,

            "company": company,

            "market": {
                "current_price": info.get("currentPrice"),
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "volume": info.get("volume"),
                "average_volume": info.get("averageVolume"),
                "market_cap": info.get("marketCap"),
            },

            "valuation": {
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales": info.get(
                    "priceToSalesTrailing12Months"
                ),
                "enterprise_value": info.get("enterpriseValue"),
                "ev_to_revenue": info.get("enterpriseToRevenue"),
                "ev_to_ebitda": info.get("enterpriseToEbitda"),
            },
        }

    # ========================================================================
    # Raw company information
    # ========================================================================

    def get_info(
        self,
        ticker_obj: yf.Ticker,
        *,
        requested_ticker: str | None = None,
    ) -> Dict[str, Any]:
        """
        Return the complete Yahoo Finance company information dictionary.
        """

        info = self._info_to_dict(ticker_obj.info)

        symbol = (
            info.get("symbol")
            or getattr(ticker_obj, "ticker", None)
            or requested_ticker
        )

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": symbol,
            "data": info,
        }

    # ========================================================================
    # Historical prices
    # ========================================================================

    def get_price_history(
        self,
        ticker_obj: yf.Ticker,
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Any]:
        """
        Get historical market prices.
        """

        history = ticker_obj.history(
            period=period,
            interval=interval,
            auto_adjust=False,
        )

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "period": period,
            "interval": interval,
            "data": self._dataframe_to_records(history),
        }

    # ========================================================================
    # Income statement
    # ========================================================================

    def get_income_statement(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Get annual income statement.
        """

        data = ticker_obj.income_stmt

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "data": self._dataframe_to_records(data),
        }

    # ========================================================================
    # Balance sheet
    # ========================================================================

    def get_balance_sheet(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Get annual balance sheet.
        """

        data = ticker_obj.balance_sheet

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "data": self._dataframe_to_records(data),
        }

    # ========================================================================
    # Cash flow
    # ========================================================================

    def get_cash_flow(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Get annual cash-flow statement.
        """

        data = ticker_obj.cashflow

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "data": self._dataframe_to_records(data),
        }

    # ========================================================================
    # Combined financial statements
    # ========================================================================

    def get_financials(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Get the main financial statements together.
        """

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "income_statement": self._dataframe_to_records(
                ticker_obj.income_stmt
            ),
            "balance_sheet": self._dataframe_to_records(
                ticker_obj.balance_sheet
            ),
            "cash_flow": self._dataframe_to_records(
                ticker_obj.cashflow
            ),
        }

    # ========================================================================
    # Dividends
    # ========================================================================

    def get_dividends(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Get historical dividend payments.
        """

        dividends = ticker_obj.dividends

        data: list[Dict[str, Any]] = []

        if dividends is not None and not dividends.empty:
            for date_value, value in dividends.items():
                data.append(
                    {
                        "date": (
                            date_value.isoformat()
                            if hasattr(date_value, "isoformat")
                            else str(date_value)
                        ),
                        "dividend": self._safe_value(value),
                    }
                )

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "data": data,
        }

    # ========================================================================
    # Stock splits
    # ========================================================================

    def get_splits(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Get historical stock splits.
        """

        splits = ticker_obj.splits

        data: list[Dict[str, Any]] = []

        if splits is not None and not splits.empty:
            for date_value, value in splits.items():
                data.append(
                    {
                        "date": (
                            date_value.isoformat()
                            if hasattr(date_value, "isoformat")
                            else str(date_value)
                        ),
                        "split": self._safe_value(value),
                    }
                )

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "data": data,
        }

    # ========================================================================
    # Analyst data
    # ========================================================================

    def get_analyst_data(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Retrieve available analyst-related information.
        """

        result: Dict[str, Any] = {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "recommendations": [],
            "price_targets": {},
            "earnings_estimates": [],
            "revenue_estimates": [],
        }

        try:
            recommendations = ticker_obj.recommendations

            if recommendations is not None:
                result["recommendations"] = (
                    self._dataframe_to_records(recommendations)
                )

        except Exception as exc:
            logger.warning(
                "Could not retrieve recommendations for %s: %s",
                ticker_obj.ticker,
                exc,
            )

        try:
            targets = ticker_obj.analyst_price_targets

            if isinstance(targets, dict):
                result["price_targets"] = self._info_to_dict(targets)

        except Exception as exc:
            logger.warning(
                "Could not retrieve price targets for %s: %s",
                ticker_obj.ticker,
                exc,
            )

        try:
            earnings = ticker_obj.earnings_estimate

            if earnings is not None:
                result["earnings_estimates"] = (
                    self._dataframe_to_records(earnings)
                )

        except Exception as exc:
            logger.warning(
                "Could not retrieve earnings estimates for %s: %s",
                ticker_obj.ticker,
                exc,
            )

        try:
            revenue = ticker_obj.revenue_estimate

            if revenue is not None:
                result["revenue_estimates"] = (
                    self._dataframe_to_records(revenue)
                )

        except Exception as exc:
            logger.warning(
                "Could not retrieve revenue estimates for %s: %s",
                ticker_obj.ticker,
                exc,
            )

        return self._safe_value(result)

    # ========================================================================
    # Valuation
    # ========================================================================

    def get_valuation(
        self,
        ticker_obj: yf.Ticker,
    ) -> Dict[str, Any]:
        """
        Extract commonly used valuation metrics.
        """

        info = self._info_to_dict(ticker_obj.info)

        valuation = {
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_sales": info.get(
                "priceToSalesTrailing12Months"
            ),
            "price_to_book": info.get("priceToBook"),
            "enterprise_to_revenue": info.get(
                "enterpriseToRevenue"
            ),
            "enterprise_to_ebitda": info.get(
                "enterpriseToEbitda"
            ),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "return_on_assets": info.get("returnOnAssets"),
            "return_on_equity": info.get("returnOnEquity"),
            "dividend_yield": info.get("dividendYield"),
            "dividend_rate": info.get("dividendRate"),
            "earnings_growth": info.get("earningsGrowth"),
            "revenue_growth": info.get("revenueGrowth"),
        }

        return {
            "success": True,
            "source": "yahoo_finance",
            "ticker": ticker_obj.ticker,
            "data": valuation,
        }

    # ========================================================================
    # Health check
    # ========================================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Check whether Yahoo Finance can be reached through yfinance.
        """

        try:
            ticker = yf.Ticker("AAPL")
            info = ticker.fast_info

            return {
                "healthy": info is not None,
                "provider": "yahoo_finance",
            }

        except Exception as exc:
            logger.exception(
                "Yahoo Finance health check failed: %s",
                exc,
            )

            return {
                "healthy": False,
                "provider": "yahoo_finance",
                "error": str(exc),
            }