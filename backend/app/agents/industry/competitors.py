from __future__ import annotations

from typing import List, Dict

from app.agents.industry.models import CompetitorProfile


class CompetitorAnalyzer:
    """
    Analyzes industry competitors.

    Responsibilities:
    - Identify competitors
    - Compare strengths and weaknesses
    - Analyze competitive positioning
    """


    def __init__(self):
        pass


    def analyze(
        self,
        competitors_data: List[Dict]
    ) -> List[CompetitorProfile]:
        """
        Convert raw competitor data into structured profiles.
        """

        competitors = []

        for company in competitors_data:

            competitor = CompetitorProfile(

                name=company.get(
                    "name",
                    "Unknown"
                ),

                market_position=company.get(
                    "market_position"
                ),

                strengths=company.get(
                    "strengths",
                    []
                ),

                weaknesses=company.get(
                    "weaknesses",
                    []
                ),

                market_share=company.get(
                    "market_share"
                )
            )

            competitors.append(
                competitor
            )

        return competitors



    def compare(
        self,
        competitors: List[CompetitorProfile]
    ) -> Dict:
        """
        Generate competitive comparison.
        """

        comparison = {}

        for competitor in competitors:

            comparison[competitor.name] = {

                "strengths":
                    competitor.strengths,

                "weaknesses":
                    competitor.weaknesses,

                "position":
                    competitor.market_position
            }


        return comparison