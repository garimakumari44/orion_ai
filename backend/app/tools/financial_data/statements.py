"""
app/tools/financial_data/statements.py

Financial statement normalization layer.

Converts raw provider responses into
standard financial models.
"""


from typing import Dict, Any, List


class FinancialStatementParser:
    """
    Normalize financial statements.
    """


    # --------------------------------
    # INCOME STATEMENT
    # --------------------------------


    def parse_income_statement(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:


        statements = data.get(
            "financials",
            []
        )


        normalized = []


        for item in statements:


            normalized.append({

                "period":
                    item.get("period"),

                "revenue":
                    item.get(
                        "revenue",
                        0
                    ),

                "cost_of_revenue":
                    item.get(
                        "cost_of_revenue",
                        0
                    ),

                "gross_profit":
                    item.get(
                        "gross_profit",
                        0
                    ),

                "operating_income":
                    item.get(
                        "operating_income",
                        0
                    ),

                "net_income":
                    item.get(
                        "net_income",
                        0
                    )

            })


        return {

            "type":
                "income_statement",

            "data":
                normalized

        }



    # --------------------------------
    # BALANCE SHEET
    # --------------------------------


    def parse_balance_sheet(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:


        statements = data.get(
            "financials",
            []
        )


        normalized=[]


        for item in statements:

            normalized.append({

                "period":
                    item.get("period"),


                "assets":
                    item.get(
                        "total_assets",
                        0
                    ),


                "liabilities":
                    item.get(
                        "total_liabilities",
                        0
                    ),


                "equity":
                    item.get(
                        "shareholder_equity",
                        0
                    ),


                "cash":
                    item.get(
                        "cash",
                        0
                    ),


                "debt":
                    item.get(
                        "total_debt",
                        0
                    )

            })


        return {

            "type":
                "balance_sheet",

            "data":
                normalized

        }



    # --------------------------------
    # CASH FLOW
    # --------------------------------


    def parse_cash_flow(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:


        statements=data.get(
            "financials",
            []
        )


        normalized=[]


        for item in statements:


            normalized.append({

                "period":
                    item.get("period"),


                "operating_cash_flow":
                    item.get(
                        "operating_cash_flow",
                        0
                    ),


                "capital_expenditure":
                    item.get(
                        "capital_expenditure",
                        0
                    ),


                "free_cash_flow":
                    item.get(
                        "free_cash_flow",
                        0
                    )

            })


        return {

            "type":
                "cash_flow",

            "data":
                normalized

        }