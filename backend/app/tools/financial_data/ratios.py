"""
app/tools/financial_data/ratios.py

Financial ratio calculation engine.

Calculates:
- Profitability ratios
- Liquidity ratios
- Leverage ratios
- Efficiency ratios
- Return metrics
"""


from typing import Dict, Any



class FinancialRatioEngine:
    """
    Calculates fundamental financial ratios.
    """



    # -----------------------------------------
    # PROFITABILITY RATIOS
    # -----------------------------------------


    def gross_margin(
        self,
        revenue: float,
        gross_profit: float
    ) -> float:

        if revenue == 0:
            return 0

        return round(
            gross_profit / revenue,
            4
        )



    def operating_margin(
        self,
        revenue: float,
        operating_income: float
    ) -> float:

        if revenue == 0:
            return 0

        return round(
            operating_income / revenue,
            4
        )



    def net_margin(
        self,
        revenue: float,
        net_income: float
    ) -> float:

        if revenue == 0:
            return 0

        return round(
            net_income / revenue,
            4
        )



    # -----------------------------------------
    # RETURN METRICS
    # -----------------------------------------


    def roe(
        self,
        net_income: float,
        equity: float
    ) -> float:

        """
        Return on Equity

        Measures shareholder return.
        """

        if equity == 0:
            return 0

        return round(
            net_income / equity,
            4
        )



    def roa(
        self,
        net_income: float,
        assets: float
    ) -> float:

        """
        Return on Assets
        """

        if assets == 0:
            return 0

        return round(
            net_income / assets,
            4
        )



    def roic(
        self,
        operating_income: float,
        debt: float,
        equity: float
    ) -> float:

        """
        Return on Invested Capital

        Simplified version:

        EBIT / (Debt + Equity)
        """

        invested_capital = (
            debt + equity
        )


        if invested_capital == 0:
            return 0


        return round(
            operating_income /
            invested_capital,
            4
        )



    # -----------------------------------------
    # LIQUIDITY RATIOS
    # -----------------------------------------


    def current_ratio(
        self,
        current_assets: float,
        current_liabilities: float
    ) -> float:


        if current_liabilities == 0:
            return 0


        return round(
            current_assets /
            current_liabilities,
            2
        )



    def quick_ratio(
        self,
        cash: float,
        receivables: float,
        current_liabilities: float
    ) -> float:


        if current_liabilities == 0:
            return 0


        return round(
            (
                cash +
                receivables
            )
            /
            current_liabilities,

            2
        )



    # -----------------------------------------
    # LEVERAGE RATIOS
    # -----------------------------------------


    def debt_to_equity(
        self,
        debt: float,
        equity: float
    ) -> float:


        if equity == 0:
            return 0


        return round(
            debt /
            equity,

            2
        )



    def debt_to_assets(
        self,
        debt: float,
        assets: float
    ) -> float:


        if assets == 0:
            return 0


        return round(
            debt /
            assets,

            2
        )



    def interest_coverage(
        self,
        operating_income: float,
        interest_expense: float
    ) -> float:


        if interest_expense == 0:
            return 0


        return round(
            operating_income /
            interest_expense,

            2
        )



    # -----------------------------------------
    # CASH FLOW METRICS
    # -----------------------------------------


    def free_cash_flow_margin(
        self,
        free_cash_flow: float,
        revenue: float
    ) -> float:


        if revenue == 0:
            return 0


        return round(
            free_cash_flow /
            revenue,

            4
        )



    def fcf_yield(
        self,
        free_cash_flow: float,
        market_cap: float
    ) -> float:


        if market_cap == 0:
            return 0


        return round(
            free_cash_flow /
            market_cap,

            4
        )



    # -----------------------------------------
    # COMPLETE COMPANY SNAPSHOT
    # -----------------------------------------


    def analyze(
        self,
        income: Dict[str, float],
        balance: Dict[str, float],
        cashflow: Dict[str, float]
    ) -> Dict[str, Any]:


        """
        Generate complete financial health snapshot.
        """


        return {


            "profitability": {


                "gross_margin":
                    self.gross_margin(
                        income["revenue"],
                        income["gross_profit"]
                    ),


                "operating_margin":
                    self.operating_margin(
                        income["revenue"],
                        income["operating_income"]
                    ),


                "net_margin":
                    self.net_margin(
                        income["revenue"],
                        income["net_income"]
                    )

            },


            "returns": {


                "ROE":
                    self.roe(
                        income["net_income"],
                        balance["equity"]
                    ),


                "ROA":
                    self.roa(
                        income["net_income"],
                        balance["assets"]
                    ),


                "ROIC":
                    self.roic(
                        income["operating_income"],
                        balance["debt"],
                        balance["equity"]
                    )

            },


            "leverage": {


                "debt_equity":
                    self.debt_to_equity(
                        balance["debt"],
                        balance["equity"]
                    )

            },


            "cash_flow": {


                "fcf_margin":
                    self.free_cash_flow_margin(
                        cashflow["free_cash_flow"],
                        income["revenue"]
                    )

            }

        }