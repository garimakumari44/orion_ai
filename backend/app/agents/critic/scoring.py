"""
Research Quality Scoring Engine

Evaluates the overall quality of
AI-generated equity research.
"""

from typing import Dict, Any


class QualityScoringEngine:
    """
    Generates quality scores based on:

    - Accuracy
    - Evidence quality
    - Reasoning quality
    - Citation quality
    - Completeness
    """

    def __init__(self):

        self.weights = {
            "accuracy": 0.30,
            "evidence": 0.25,
            "reasoning": 0.20,
            "citations": 0.15,
            "completeness": 0.10
        }


    def score(
        self,
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate final research score.
        """

        scores = {

            "accuracy":
                evaluation.get(
                    "accuracy",
                    0
                ),

            "evidence":
                evaluation.get(
                    "evidence",
                    0
                ),

            "reasoning":
                evaluation.get(
                    "reasoning",
                    0
                ),

            "citations":
                evaluation.get(
                    "citations",
                    0
                ),

            "completeness":
                evaluation.get(
                    "completeness",
                    0
                )
        }


        final_score = 0

        for metric, weight in self.weights.items():

            final_score += (
                scores[metric]
                *
                weight
            )


        return {

            "score":
                round(
                    final_score,
                    2
                ),

            "rating":
                self.rating(
                    final_score
                ),

            "breakdown":
                scores
        }



    def rating(
        self,
        score: float
    ) -> str:

        if score >= 0.85:
            return "excellent"

        if score >= 0.70:
            return "good"

        if score >= 0.50:
            return "needs_review"

        return "poor"