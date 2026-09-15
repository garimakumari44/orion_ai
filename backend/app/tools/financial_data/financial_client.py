"""
app/tools/financial_data/financial_client.py

Financial Data Client

Purpose:
    Abstracts external financial data providers.

Used by:
    - Financial Agent
    - Valuation Agent
    - Risk Agent
    - Company Agent

Future providers:
    - SEC XBRL
    - Financial Modeling Prep
    - Alpha Vantage
    - Polygon
    - Yahoo Finance
"""


from typing import Dict, Any, Optional
import requests
import logging


logger = logging.getLogger(__name__)


class FinancialDataClient:
    """
    Base client for financial data retrieval.
    """


    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 15
    ):

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout



    # =====================================================
    # INTERNAL REQUEST HANDLER
    # =====================================================


    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        """
        Execute GET request.

        All external requests pass through here.
        """


        if params is None:
            params = {}


        if self.api_key:

            params["apikey"] = self.api_key



        url = (
            f"{self.base_url}/{endpoint}"
        )


        try:

            response = requests.get(
                url,
                params=params,
                timeout=self.timeout
            )


            response.raise_for_status()


            return response.json()



        except requests.exceptions.Timeout:

            logger.error(
                "Financial API timeout"
            )

            return {
                "success": False,
                "error": "timeout"
            }



        except requests.exceptions.RequestException as error:

            logger.error(
                f"Financial API error: {error}"
            )

            return {
                "success": False,
                "error": str(error)
            }



    # =====================================================
    # COMPANY DATA
    # =====================================================


    def company_profile(
        self,
        ticker: str
    ) -> Dict[str, Any]:

        """
        Get company information.

        Example:
            Apple
            Microsoft
            Nvidia
        """


        return self._get(

            "company/profile",

            {
                "symbol": ticker
            }

        )



    # =====================================================
    # FINANCIAL STATEMENTS
    # =====================================================


    def income_statement(
        self,
        ticker: str,
        period: str = "annual"
    ) -> Dict[str, Any]:


        return self._get(

            "financials/income",

            {
                "symbol": ticker,
                "period": period
            }

        )



    def balance_sheet(
        self,
        ticker: str,
        period: str = "annual"
    ) -> Dict[str, Any]:


        return self._get(

            "financials/balance-sheet",

            {
                "symbol": ticker,
                "period": period
            }

        )



    def cash_flow_statement(
        self,
        ticker: str,
        period: str = "annual"
    ) -> Dict[str, Any]:


        return self._get(

            "financials/cash-flow",

            {
                "symbol": ticker,
                "period": period
            }

        )



    # =====================================================
    # MARKET DATA
    # =====================================================


    def stock_price(
        self,
        ticker: str
    ) -> Dict[str, Any]:


        return self._get(

            "market/price",

            {
                "symbol": ticker
            }

        )



    def historical_prices(
        self,
        ticker: str,
        range: str = "1y"
    ) -> Dict[str, Any]:


        return self._get(

            "market/history",

            {
                "symbol": ticker,
                "range": range
            }

        )



    def market_snapshot(
        self,
        ticker: str
    ) -> Dict[str, Any]:

        """
        Quick market overview.
        """


        return self._get(

            "market/snapshot",

            {
                "symbol": ticker
            }

        )



    # =====================================================
    # VALUATION DATA
    # =====================================================


    def valuation_metrics(
        self,
        ticker: str
    ) -> Dict[str, Any]:


        """
        Fetch:

        - PE ratio
        - EV/EBITDA
        - Price/Sales
        - Market Cap
        - Enterprise Value
        """


        return self._get(

            "valuation/metrics",

            {
                "symbol": ticker
            }

        )



    # =====================================================
    # COMPANY RESEARCH BUNDLE
    # =====================================================


    def full_company_snapshot(
        self,
        ticker: str
    ) -> Dict[str, Any]:


        """
        Collect all major company data.

        Used by:
            Company Agent
            Financial Agent
        """


        return {


            "profile":
                self.company_profile(
                    ticker
                ),


            "income_statement":
                self.income_statement(
                    ticker
                ),


            "balance_sheet":
                self.balance_sheet(
                    ticker
                ),


            "cash_flow":
                self.cash_flow_statement(
                    ticker
                ),


            "market":
                self.market_snapshot(
                    ticker
                ),


            "valuation":
                self.valuation_metrics(
                    ticker
                )

        }