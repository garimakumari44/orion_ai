from __future__ import annotations

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Generates final investment recommendation.

    Converts:
    - committee votes
    - debate outcome
    - valuation
    - risks
    - catalysts

    into an investment decision.
    """

    RECOMMENDATIONS = [
        "STRONG BUY",
        "BUY",
        "HOLD",
        "SELL",
        "STRONG SELL"
    ]


    def __init__(self):

        self.default_recommendation = "HOLD"



    async def generate(
        self,
        committee_result: Dict[str, Any]
    ) -> Dict[str, Any]:

        """
        Generate final recommendation.
        """


        votes = committee_result.get(
            "votes",
            []
        )


        recommendation = self.calculate_recommendation(
            votes
        )


        return {

            "recommendation":
                recommendation,

            "investment_action":
                self.get_action(
                    recommendation
                ),

            "summary":
                "Recommendation generated from investment committee analysis"

        }



    def calculate_recommendation(
        self,
        votes
    ) -> str:


        if not votes:
            return self.default_recommendation


        buy_score = 0
        sell_score = 0


        for vote in votes:

            decision = vote.get(
                "vote"
            )


            if decision in [
                "BUY",
                "STRONG BUY"
            ]:
                buy_score += 1


            elif decision in [
                "SELL",
                "STRONG SELL"
            ]:
                sell_score += 1



        if buy_score > sell_score:

            return "BUY"


        if sell_score > buy_score:

            return "SELL"


        return "HOLD"



    def get_action(
        self,
        recommendation: str
    ):


        actions = {

            "STRONG BUY":
                "Increase position",

            "BUY":
                "Consider adding position",

            "HOLD":
                "Maintain position",

            "SELL":
                "Reduce exposure",

            "STRONG SELL":
                "Exit position"

        }


        return actions.get(
            recommendation,
            "Review"
        )