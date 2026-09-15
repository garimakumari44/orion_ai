"""
app/financial/providers/provider_manager.py

Financial Provider Manager.

Responsibilities
----------------

- Register financial providers.
- Select financial providers.
- Execute normalized financial-data requests.
- Provide Yahoo Finance through YahooFinanceTool.
- Keep provider/tool orchestration outside agents.

Architecture
------------

FinancialResearchService
        |
        v
FinancialProviderManager
        |
        +----------------------+
        |                      |
        v                      v
FinancialProvider       YahooFinanceTool
        |                      |
        v                      v
   External APIs            yfinance

Important
---------

This manager does NOT:

- create AgentContext
- execute agents
- create tasks
- manage ExecutionEngine
- access ResearchRepository
- contain research-agent logic
- resolve canonical Company records
- perform industry research
- construct domain services
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from app.financial.providers.base import BaseProvider
from app.tools.market.yahoo_finance_tool import YahooFinanceTool


logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================


class FinancialProviderError(Exception):
    """
    Base exception for financial provider failures.
    """


class FinancialProviderNotFoundError(FinancialProviderError):
    """
    Raised when a requested financial provider is unavailable.
    """


# ============================================================================
# Financial Provider Manager
# ============================================================================


class FinancialProviderManager:
    """
    Central financial-provider manager.

    The manager exposes Yahoo Finance through YahooFinanceTool
    and supports additional FinancialProvider implementations.

    The manager owns provider/tool orchestration only.

    It does not own:

        AgentContext
        AgentManager
        ExecutionEngine
        ResearchRepository
        CompanyRepository
        IndustryResearchService
        CompanyResearchService
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(
        self,
        *,
        yahoo_finance_tool: YahooFinanceTool | None = None,
    ) -> None:
        """
        Initialize the financial provider manager.

        Parameters
        ----------
        yahoo_finance_tool:
            Optional YahooFinanceTool instance.

            Dependency injection is supported so tests and alternative
            implementations can provide their own tool.
        """

        self.yahoo_finance_tool = (
            yahoo_finance_tool
            if yahoo_finance_tool is not None
            else YahooFinanceTool()
        )

        self._providers: dict[
            str,
            BaseProvider,
        ] = {}

    # ========================================================================
    # Provider Registration
    # ========================================================================

    def register(
        self,
        provider: BaseProvider,
    ) -> None:
        """
        Register a financial provider.

        Parameters
        ----------
        provider:
            Financial provider implementation.

        Raises
        ------
        TypeError
            If the supplied object is not a BaseProvider.

        ValueError
            If the provider name is empty.
        """

        if not isinstance(provider, BaseProvider):
            raise TypeError(
                "Provider must inherit from BaseProvider."
            )

        name = getattr(
            provider,
            "name",
            None,
        )

        if not isinstance(name, str):
            raise TypeError(
                "Financial provider must define a string 'name'."
            )

        name = name.strip().lower()

        if not name:
            raise ValueError(
                "Financial provider name cannot be empty."
            )

        self._providers[name] = provider

        logger.info(
            "Financial provider registered | provider=%s",
            name,
        )

    # ========================================================================
    # Provider Lookup
    # ========================================================================

    def get_provider(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Return a registered provider.
        """

        if not name:
            raise ValueError(
                "Provider name is required."
            )

        normalized_name = name.strip().lower()

        provider = self._providers.get(
            normalized_name
        )

        if provider is None:
            raise FinancialProviderNotFoundError(
                f"Financial provider '{normalized_name}' "
                f"is not registered. "
                f"Available providers: "
                f"{self.list_providers()}"
            )

        return provider

    # ========================================================================
    # Provider Existence
    # ========================================================================

    def has_provider(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a financial provider is registered.
        """

        if not name:
            return False

        return (
            name.strip().lower()
            in self._providers
        )

    # ========================================================================
    # Provider Listing
    # ========================================================================

    def list_providers(self) -> list[str]:
        """
        Return registered provider names.
        """

        return sorted(
            self._providers.keys()
        )

    # ========================================================================
    # Capability Lookup
    # ========================================================================

    def get_provider_for_capability(
        self,
        capability: str,
    ) -> BaseProvider:
        """
        Find the first registered provider supporting
        the requested capability.
        """

        if not capability:
            raise ValueError(
                "Capability is required."
            )

        normalized_capability = (
            capability.strip().lower()
        )

        if not normalized_capability:
            raise ValueError(
                "Capability cannot be empty."
            )

        for provider in self._providers.values():
            try:
                supports = getattr(
                    provider,
                    "supports",
                    None,
                )

                if not callable(supports):
                    continue

                if supports(
                    normalized_capability
                ):
                    return provider

            except Exception:
                logger.exception(
                    "Financial provider capability check failed | "
                    "provider=%s | capability=%s",
                    getattr(
                        provider,
                        "name",
                        provider.__class__.__name__,
                    ),
                    normalized_capability,
                )

        raise FinancialProviderError(
            "No financial provider supports "
            f"capability '{normalized_capability}'."
        )

    # ========================================================================
    # Yahoo Finance
    # ========================================================================

    async def get_yahoo_financial_data(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve normalized financial data from Yahoo Finance.

        YahooFinanceTool is responsible for communication with
        Yahoo/yfinance.

        This manager is responsible for:

        1. Resolving/validating the ticker.
        2. Executing required Yahoo operations.
        3. Validating tool responses.
        4. Normalizing responses into the canonical
           financial-data contract.
        """

        resolved_ticker = self._resolve_ticker(
            company=company,
            ticker=ticker,
        )

        if not resolved_ticker:
            raise ValueError(
                "Yahoo Finance requires a ticker symbol."
            )

        logger.info(
            "Yahoo Finance request started | "
            "company=%r | ticker=%r",
            company,
            resolved_ticker,
        )

        # --------------------------------------------------------------------
        # Overview
        # --------------------------------------------------------------------

        overview = await self._execute_yahoo_tool(
            ticker=resolved_ticker,
            operation="overview",
        )

        self._raise_if_failed(
            result=overview,
            operation="overview",
            ticker=resolved_ticker,
        )

        # --------------------------------------------------------------------
        # Financial Statements
        # --------------------------------------------------------------------

        financials = await self._execute_yahoo_tool(
            ticker=resolved_ticker,
            operation="financials",
        )

        self._raise_if_failed(
            result=financials,
            operation="financials",
            ticker=resolved_ticker,
        )

        # --------------------------------------------------------------------
        # Valuation
        # --------------------------------------------------------------------

        valuation = await self._execute_yahoo_tool(
            ticker=resolved_ticker,
            operation="valuation",
        )

        self._raise_if_failed(
            result=valuation,
            operation="valuation",
            ticker=resolved_ticker,
        )

        # --------------------------------------------------------------------
        # Normalize
        # --------------------------------------------------------------------

        normalized = self._normalize_yahoo_response(
            company=company,
            ticker=resolved_ticker,
            overview=overview,
            financials=financials,
            valuation=valuation,
        )

        logger.info(
            "Yahoo Finance request completed | "
            "company=%r | ticker=%r",
            company,
            resolved_ticker,
        )

        return normalized

    # ========================================================================
    # Yahoo Tool Execution
    # ========================================================================

    async def _execute_yahoo_tool(
        self,
        *,
        ticker: str,
        operation: str,
    ) -> Any:
        """
        Execute YahooFinanceTool safely.

        Supports both synchronous and asynchronous execute()
        implementations.
        """

        try:
            result = self.yahoo_finance_tool.execute(
                ticker=ticker,
                operation=operation,
            )

            if inspect.isawaitable(result):
                result = await result

            return result

        except FinancialProviderError:
            raise

        except Exception as exc:
            logger.exception(
                "Yahoo Finance tool execution failed | "
                "ticker=%s | operation=%s",
                ticker,
                operation,
            )

            raise FinancialProviderError(
                f"Yahoo Finance {operation} failed "
                f"for {ticker}: {exc}"
            ) from exc

    # ========================================================================
    # Generic Financial Data API
    # ========================================================================

    async def get_financial_data(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
        provider: str = "yahoo_finance",
    ) -> dict[str, Any]:
        """
        Canonical financial-data entry point.

        Yahoo Finance is the default provider.

        Additional registered providers can be introduced without
        changing FinancialResearchService.
        """

        normalized_provider = (
            provider.strip().lower()
            if provider
            else "yahoo_finance"
        )

        # --------------------------------------------------------------------
        # Canonical Yahoo Finance path
        # --------------------------------------------------------------------

        if normalized_provider in {
            "yahoo",
            "yahoo_finance",
            "yfinance",
        }:
            return await self.get_yahoo_financial_data(
                company=company,
                ticker=ticker,
            )

        # --------------------------------------------------------------------
        # Registered providers
        # --------------------------------------------------------------------

        if not self.has_provider(
            normalized_provider
        ):
            raise FinancialProviderNotFoundError(
                f"Financial provider '{normalized_provider}' "
                f"is not available. "
                f"Available providers: "
                f"{self.list_providers()}"
            )

        registered_provider = self.get_provider(
            normalized_provider
        )

        get_financial_data = getattr(
            registered_provider,
            "get_financial_data",
            None,
        )

        if not callable(get_financial_data):
            raise FinancialProviderError(
                f"Financial provider "
                f"'{normalized_provider}' does not implement "
                "get_financial_data()."
            )

        try:
            result = get_financial_data(
                company=company,
                ticker=ticker,
            )

            if inspect.isawaitable(result):
                result = await result

            if not isinstance(result, dict):
                raise FinancialProviderError(
                    f"Financial provider "
                    f"'{normalized_provider}' returned "
                    "invalid data."
                )

            return result

        except FinancialProviderError:
            raise

        except Exception as exc:
            logger.exception(
                "Financial provider failed | "
                "provider=%s | company=%r | ticker=%r",
                normalized_provider,
                company,
                ticker,
            )

            raise FinancialProviderError(
                f"Financial provider "
                f"'{normalized_provider}' failed: {exc}"
            ) from exc

    # ========================================================================
    # Ticker Resolution
    # ========================================================================

    @staticmethod
    def _resolve_ticker(
        *,
        company: str | None,
        ticker: str | None,
    ) -> str | None:
        """
        Resolve the ticker.

        This manager intentionally does not guess ticker symbols
        from arbitrary company names.

        Canonical ticker resolution should happen upstream,
        normally through Company/ResearchService.
        """

        if ticker:
            normalized = ticker.strip().upper()

            if normalized:
                return normalized

        if company:
            logger.warning(
                "Company supplied without ticker. "
                "Ticker resolution should happen upstream | "
                "company=%r",
                company,
            )

        return None

    # ========================================================================
    # Error Handling
    # ========================================================================

    @staticmethod
    def _raise_if_failed(
        *,
        result: Any,
        operation: str,
        ticker: str,
    ) -> None:
        """
        Convert YahooFinanceTool failures into
        FinancialProviderError.
        """

        if not isinstance(
            result,
            dict,
        ):
            raise FinancialProviderError(
                f"Yahoo Finance returned invalid data "
                f"for {ticker} during {operation}."
            )

        if result.get("success") is False:
            error = result.get(
                "error",
                "Unknown Yahoo Finance error.",
            )

            raise FinancialProviderError(
                f"Yahoo Finance {operation} failed "
                f"for {ticker}: {error}"
            )

    # ========================================================================
    # Yahoo Response Normalization
    # ========================================================================

    @staticmethod
    def _normalize_yahoo_response(
        *,
        company: str | None,
        ticker: str,
        overview: dict[str, Any],
        financials: dict[str, Any],
        valuation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize YahooFinanceTool responses into the
        canonical financial-data structure.
        """

        # --------------------------------------------------------------------
        # Overview
        # --------------------------------------------------------------------

        overview_data = (
            overview.get("company", {})
            if isinstance(overview, dict)
            else {}
        )

        market_data = (
            overview.get("market", {})
            if isinstance(overview, dict)
            else {}
        )

        # --------------------------------------------------------------------
        # Valuation
        # --------------------------------------------------------------------

        valuation_data = (
            valuation.get("data", {})
            if isinstance(valuation, dict)
            else {}
        )

        # --------------------------------------------------------------------
        # Financial Statements
        # --------------------------------------------------------------------

        financials_data = (
            financials
            if isinstance(financials, dict)
            else {}
        )

        income_statement = financials_data.get(
            "income_statement",
            [],
        )

        balance_sheet = financials_data.get(
            "balance_sheet",
            [],
        )

        cash_flow_statement = financials_data.get(
            "cash_flow",
            [],
        )

        # --------------------------------------------------------------------
        # Defensive normalization
        # --------------------------------------------------------------------

        if not isinstance(
            overview_data,
            dict,
        ):
            overview_data = {}

        if not isinstance(
            market_data,
            dict,
        ):
            market_data = {}

        if not isinstance(
            valuation_data,
            dict,
        ):
            valuation_data = {}

        if not isinstance(
            income_statement,
            (dict, list),
        ):
            income_statement = []

        if not isinstance(
            balance_sheet,
            (dict, list),
        ):
            balance_sheet = []

        if not isinstance(
            cash_flow_statement,
            (dict, list),
        ):
            cash_flow_statement = []

        # --------------------------------------------------------------------
        # Company Identity
        # --------------------------------------------------------------------

        company_name = (
            overview_data.get("name")
            or company
            or ticker
        )

        resolved_symbol = (
            overview_data.get("symbol")
            or ticker
        )

        # --------------------------------------------------------------------
        # Canonical Response
        # --------------------------------------------------------------------

        return {
            "company": company_name,
            "company_name": company_name,
            "ticker": resolved_symbol,

            "industry": overview_data.get(
                "industry"
            ),

            "sector": overview_data.get(
                "sector"
            ),

            "country": overview_data.get(
                "country"
            ),

            "exchange": overview_data.get(
                "exchange"
            ),

            "currency": overview_data.get(
                "currency"
            ),

            "description": overview_data.get(
                "description"
            ),

            "income_statement": income_statement,

            "balance_sheet": balance_sheet,

            "cash_flow_statement": cash_flow_statement,

            "financial_metrics": {
                **market_data,
                **valuation_data,
            },

            "sources": [
                {
                    "provider": "yahoo_finance",
                    "type": "financial_market_data",
                }
            ],
        }

    # ========================================================================
    # Health Check
    # ========================================================================

    async def health_check(
        self,
    ) -> dict[str, bool]:
        """
        Check availability of configured financial sources.

        If YahooFinanceTool exposes health_check(), it is used.

        Otherwise Yahoo Finance is considered configured and
        available until an actual request fails.
        """

        result: dict[str, bool] = {
            "yahoo_finance": False,
        }

        try:
            health_check = getattr(
                self.yahoo_finance_tool,
                "health_check",
                None,
            )

            if callable(health_check):
                health_result = health_check()

                if inspect.isawaitable(
                    health_result
                ):
                    health_result = await health_result

                result["yahoo_finance"] = bool(
                    health_result
                )

            else:
                result["yahoo_finance"] = True

        except Exception:
            logger.exception(
                "Yahoo Finance health check failed."
            )

            result["yahoo_finance"] = False

        # --------------------------------------------------------------------
        # Registered Providers
        # --------------------------------------------------------------------

        for provider_name, provider in (
            self._providers.items()
        ):
            try:
                provider_health_check = getattr(
                    provider,
                    "health_check",
                    None,
                )

                if callable(
                    provider_health_check
                ):
                    health_result = (
                        provider_health_check()
                    )

                    if inspect.isawaitable(
                        health_result
                    ):
                        health_result = (
                            await health_result
                        )

                    result[provider_name] = bool(
                        health_result
                    )

                else:
                    result[provider_name] = True

            except Exception:
                logger.exception(
                    "Financial provider health check failed | "
                    "provider=%s",
                    provider_name,
                )

                result[provider_name] = False

        return result


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "FinancialProviderManager",
    "FinancialProviderError",
    "FinancialProviderNotFoundError",
]