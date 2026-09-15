"""
Candidate output comparison engine.

Compares multiple AI outputs based on evaluation
scores, quality metrics, and detected issues.
"""

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class CandidateComparison:
    """
    Represents comparison result between candidates.
    """

    winner: str
    ranking: List[str]
    score_difference: Dict[str, float]
    analysis: Dict[str, Any]


class OutputComparator:
    """
    Compare candidate AI outputs.

    Example:
        Candidate A:
            factuality: 0.9
            coherence: 0.8

        Candidate B:
            factuality: 0.7
            coherence: 0.95

    Produces ranked output.
    """

    def __init__(self):
        self.history = []


    def compare(
        self,
        candidates: Dict[str, Dict[str, float]]
    ) -> CandidateComparison:
        """
        Compare candidate scores.

        Args:
            candidates:
                {
                    "candidate_1": {
                        "accuracy":0.9,
                        "clarity":0.8
                    }
                }

        Returns:
            CandidateComparison
        """

        scores = {}

        for name, metrics in candidates.items():

            if not metrics:
                scores[name] = 0
                continue

            scores[name] = sum(
                metrics.values()
            ) / len(metrics)


        ranking = sorted(
            scores.keys(),
            key=lambda x: scores[x],
            reverse=True
        )


        winner = ranking[0]


        difference = {}

        best_score = scores[winner]

        for name, score in scores.items():
            difference[name] = round(
                best_score - score,
                4
            )


        analysis = {
            "total_candidates": len(candidates),
            "best_score": best_score,
            "average_score": (
                sum(scores.values())
                /
                len(scores)
            )
        }


        result = CandidateComparison(
            winner=winner,
            ranking=ranking,
            score_difference=difference,
            analysis=analysis
        )


        self.history.append(result)

        return result



    def best_candidate(
        self,
        candidates: Dict[str, Dict[str,float]]
    ):
        """
        Return highest scoring candidate.
        """

        result = self.compare(candidates)

        return result.winner



    def improvement_delta(
        self,
        previous: Dict[str,float],
        current: Dict[str,float]
    ):
        """
        Measure improvement between versions.

        Example:

        old:
        accuracy=0.7

        new:
        accuracy=0.9

        delta:
        +0.2
        """

        delta={}

        keys=set(previous)|set(current)


        for key in keys:

            old=previous.get(
                key,
                0
            )

            new=current.get(
                key,
                0
            )

            delta[key]=round(
                new-old,
                4
            )


        return delta