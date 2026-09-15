"""
Source Quality Evaluation

Ranks reliability of evidence sources.
"""


from typing import Dict, Any



class SourceQualityEvaluator:
    """
    Evaluates source credibility.

    Used before passing evidence
    to Critic Agent.
    """



    SOURCE_SCORES = {

        "sec":
            1.0,

        "annual_report":
            0.95,

        "earnings_call":
            0.90,

        "company_release":
            0.85,

        "financial_database":
            0.80,

        "reputable_news":
            0.75,

        "blog":
            0.40,

        "unknown":
            0.20
    }



    def evaluate(
        self,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:

        source_type = (
            source.get(
                "type",
                "unknown"
            )
            .lower()
        )


        score = self.SOURCE_SCORES.get(
            source_type,
            0.2
        )


        return {

            "source":
                source.get(
                    "name"
                ),

            "quality_score":
                score,

            "rating":
                self.rating(
                    score
                )

        }




    def rating(
        self,
        score: float
    ) -> str:

        if score >= 0.9:
            return "excellent"

        if score >= 0.75:
            return "good"

        if score >= 0.5:
            return "acceptable"

        return "weak"