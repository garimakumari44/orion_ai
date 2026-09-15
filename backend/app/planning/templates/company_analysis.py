"""
Company Analysis Template

Multi-Agent Equity Research Workflow.

Example:

Analyze Tesla

Agents:

1. Company Research Agent
2. Financial Agent
3. Market Agent
4. Risk Agent
5. Valuation Agent
6. Report Agent
"""

from typing import List, Dict



def company_analysis_template(
    company: str
) -> List[Dict]:

    return [

        {
            "id": "company_profile",
            "name": "Analyze Company Profile",
            "agent": "company_research_agent",
            "task_type": "research",

            "input": {
                "company": company
            },

            "dependencies": []
        },


        {
            "id": "financial_analysis",
            "name": "Analyze Financial Performance",
            "agent": "financial_agent",

            "task_type": "financial_analysis",

            "tools":[
                "financial_database",
                "market_data"
            ],

            "dependencies":[
                "company_profile"
            ]
        },


        {
            "id": "business_analysis",
            "name": "Analyze Business Model",
            "agent":"business_agent",

            "task_type":"strategy_analysis",

            "dependencies":[
                "company_profile"
            ]
        },


        {
            "id":"competitive_analysis",
            "name":"Analyze Competition",

            "agent":"market_agent",

            "task_type":"competitive_intelligence",

            "dependencies":[
                "business_analysis"
            ]
        },


        {
            "id":"risk_analysis",

            "name":"Identify Investment Risks",

            "agent":"risk_agent",

            "task_type":"risk_assessment",

            "dependencies":[
                "financial_analysis",
                "competitive_analysis"
            ]
        },


        {
            "id":"valuation",

            "name":"Perform Valuation Analysis",

            "agent":"valuation_agent",

            "task_type":"valuation",

            "tools":[
                "financial_model"
            ],

            "dependencies":[
                "financial_analysis"
            ]
        },


        {
            "id":"investment_report",

            "name":"Generate Equity Research Report",

            "agent":"equity_report_agent",

            "task_type":"report_generation",

            "dependencies":[
                "risk_analysis",
                "valuation"
            ]
        }

    ]