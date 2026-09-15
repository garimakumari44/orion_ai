from __future__ import annotations

from typing import List, Dict

from app.agents.industry.models import IndustryTrend



class TrendAnalyzer:
    """
    Analyzes industry trends.

    Covers:
    - Technology shifts
    - Regulations
    - Consumer behavior
    - Future opportunities
    """


    def __init__(self):
        pass



    def analyze(
        self,
        trends_data: List[Dict]
    ) -> List[IndustryTrend]:
        """
        Convert raw trends into structured objects.
        """

        trends = []


        for item in trends_data:

            trend = IndustryTrend(

                name=item.get(
                    "name",
                    "Unknown"
                ),

                impact=item.get(
                    "impact",
                    "Unknown"
                ),

                description=item.get(
                    "description"
                )
            )


            trends.append(
                trend
            )


        return trends



    def identify_opportunities(
        self,
        trends: List[IndustryTrend]
    ) -> List[str]:
        """
        Extract positive industry opportunities.
        """

        opportunities = []


        for trend in trends:

            if trend.impact.lower() in [
                "positive",
                "high"
            ]:
                opportunities.append(
                    trend.name
                )


        return opportunities



    def identify_risks(
        self,
        trends: List[IndustryTrend]
    ) -> List[str]:
        """
        Extract negative industry trends.
        """

        risks = []


        for trend in trends:

            if trend.impact.lower() in [
                "negative",
                "low"
            ]:
                risks.append(
                    trend.name
                )


        return risks