"""
Startup Equity Analysis Template

Used for:

- Startup due diligence
- Venture investment analysis
- Seed / Series A / Growth analysis

Agents:

Startup Research Agent
Market Agent
Founder Agent
Financial Agent
Risk Agent
Investment Memo Agent
"""

from typing import List, Dict



def startup_equity_analysis_template(
    startup: str
) -> List[Dict]:


    return [

        {
            "id": "startup_profile",

            "name":
            "Analyze Startup Profile",

            "agent":
            "startup_research_agent",

            "task_type":
            "startup_research",

            "input":{
                "startup": startup
            },

            "dependencies":[]
        },


        {
            "id":"founder_analysis",

            "name":
            "Analyze Founders and Team",

            "agent":
            "founder_intelligence_agent",

            "task_type":
            "team_analysis",

            "dependencies":[
                "startup_profile"
            ]
        },


        {
            "id":"market_analysis",

            "name":
            "Analyze Market Opportunity",

            "agent":
            "market_analysis_agent",

            "task_type":
            "market_research",

            "dependencies":[
                "startup_profile"
            ]
        },


        {
            "id":"business_model",

            "name":
            "Analyze Business Model",

            "agent":
            "business_model_agent",

            "task_type":
            "business_analysis",

            "dependencies":[
                "startup_profile"
            ]
        },


        {
            "id":"startup_financials",

            "name":
            "Analyze Startup Financials",

            "agent":
            "startup_financial_agent",

            "task_type":
            "financial_analysis",

            "dependencies":[
                "business_model"
            ]
        },


        {
            "id":"investment_risk",

            "name":
            "Identify Investment Risks",

            "agent":
            "risk_agent",

            "task_type":
            "risk_assessment",

            "dependencies":[
                "market_analysis",
                "startup_financials"
            ]
        },


        {
            "id":"startup_investment_memo",

            "name":
            "Generate Investment Memo",

            "agent":
            "investment_memo_agent",

            "task_type":
            "report_generation",

            "dependencies":[
                "founder_analysis",
                "investment_risk"
            ]
        }

    ]