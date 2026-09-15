"""
Financial Analysis Template

Deep financial research workflow.

Used by:

- Equity Analyst Agent
- Valuation Agent
- Investment Agent
"""

from typing import List, Dict



def financial_analysis_template(
    company: str
) -> List[Dict]:


    return [

        {
            "id":
            "financial_data_collection",

            "name":
            "Collect Financial Data",

            "agent":
            "financial_data_agent",

            "task_type":
            "data_retrieval",

            "input":{
                "company":company
            },

            "tools":[
                "financial_database",
                "market_api"
            ],

            "dependencies":[]
        },


        {
            "id":
            "income_statement_analysis",

            "name":
            "Analyze Income Statement",

            "agent":
            "financial_statement_agent",

            "task_type":
            "income_analysis",

            "dependencies":[
                "financial_data_collection"
            ]
        },


        {
            "id":
            "balance_sheet_analysis",

            "name":
            "Analyze Balance Sheet",

            "agent":
            "financial_statement_agent",

            "task_type":
            "balance_sheet_analysis",

            "dependencies":[
                "financial_data_collection"
            ]
        },


        {
            "id":
            "cashflow_analysis",

            "name":
            "Analyze Cash Flow",

            "agent":
            "financial_statement_agent",

            "task_type":
            "cashflow_analysis",

            "dependencies":[
                "financial_data_collection"
            ]
        },


        {
            "id":
            "financial_ratios",

            "name":
            "Calculate Financial Ratios",

            "agent":
            "quant_agent",

            "task_type":
            "ratio_analysis",

            "dependencies":[
                "income_statement_analysis",
                "balance_sheet_analysis",
                "cashflow_analysis"
            ]
        },


        {
            "id":
            "forecast_model",

            "name":
            "Build Financial Forecast",

            "agent":
            "forecasting_agent",

            "task_type":
            "financial_modeling",

            "dependencies":[
                "financial_ratios"
            ]
        },


        {
            "id":
            "financial_report",

            "name":
            "Generate Financial Report",

            "agent":
            "equity_report_agent",

            "task_type":
            "report_generation",

            "dependencies":[
                "forecast_model"
            ]
        }

    ]