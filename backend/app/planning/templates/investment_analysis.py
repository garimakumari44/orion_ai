"""
Investment Analysis Template

Produces:

- Buy/Sell/Hold analysis
- Investment thesis
- Risk evaluation
- Expected return analysis
"""

from typing import List, Dict



def investment_analysis_template(
    asset: str
) -> List[Dict]:


    return [

        {
            "id":
            "investment_thesis",

            "name":
            "Generate Investment Thesis",

            "agent":
            "investment_strategy_agent",

            "task_type":
            "thesis_generation",

            "input":{
                "asset":asset
            },

            "dependencies":[]
        },


        {
            "id":
            "market_position",

            "name":
            "Analyze Market Position",

            "agent":
            "market_agent",

            "task_type":
            "market_analysis",

            "dependencies":[
                "investment_thesis"
            ]
        },


        {
            "id":
            "financial_health",

            "name":
            "Analyze Financial Health",

            "agent":
            "financial_agent",

            "task_type":
            "financial_analysis",

            "dependencies":[]
        },


        {
            "id":
            "valuation_analysis",

            "name":
            "Analyze Valuation",

            "agent":
            "valuation_agent",

            "task_type":
            "valuation",

            "dependencies":[
                "financial_health"
            ]
        },


        {
            "id":
            "investment_risk",

            "name":
            "Evaluate Investment Risk",

            "agent":
            "risk_agent",

            "task_type":
            "risk_analysis",

            "dependencies":[
                "market_position",
                "valuation_analysis"
            ]
        },


        {
            "id":
            "investment_decision",

            "name":
            "Create Investment Decision",

            "agent":
            "portfolio_agent",

            "task_type":
            "investment_recommendation",

            "dependencies":[
                "investment_risk"
            ]
        }

    ]