"""
Company Comparison Template

Used for:

- Stock comparison
- Competitor analysis
- Investment decisions

Example:

Compare:
Apple vs Microsoft
"""

from typing import List, Dict



def company_comparison_template(
    companies: List[str]
) -> List[Dict]:


    tasks=[]


    analysis_ids=[]


    for company in companies:


        task_id = (
            f"analyze_{company.lower()}"
            .replace(" ","_")
        )


        analysis_ids.append(task_id)


        tasks.append(

            {
                "id":task_id,

                "name":
                f"Analyze {company}",

                "agent":
                "company_analysis_agent",

                "task_type":
                "company_analysis",


                "input":{
                    "company":company
                },


                "dependencies":[]

            }

        )



    tasks.append(

        {

            "id":
            "comparison_analysis",


            "name":
            "Compare Companies",


            "agent":
            "comparison_agent",


            "task_type":
            "comparative_analysis",


            "dependencies":
            analysis_ids

        }

    )


    tasks.append(

        {

            "id":
            "final_investment_report",


            "name":
            "Generate Investment Recommendation",


            "agent":
            "equity_report_agent",


            "task_type":
            "investment_report",


            "dependencies":[
                "comparison_analysis"
            ]

        }

    )


    return tasks