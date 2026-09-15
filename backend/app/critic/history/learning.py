"""
Learning module.

Analyzes historical evaluations
and identifies improvement patterns.
"""

from collections import defaultdict
from typing import List, Dict, Any


class EvaluationLearner:
    """
    Learns from previous evaluation results.
    """


    def __init__(self):

        self.records=[]



    def add_record(
        self,
        evaluation: Dict[str,Any]
    ):
        """
        Store evaluation result.

        Example:

        {
          "score":0.8,
          "issues":[
             "hallucination",
             "weak citation"
          ]
        }

        """

        self.records.append(
            evaluation
        )



    def failure_patterns(self):
        """
        Find common failures.

        Returns:

        {
          "hallucination":5,
          "citation":3
        }

        """

        failures=defaultdict(int)


        for record in self.records:

            issues=record.get(
                "issues",
                []
            )

            for issue in issues:

                failures[issue]+=1


        return dict(
            failures
        )



    def metric_trends(self):
        """
        Track metric improvement.

        Example:

        accuracy:
            [
              0.7,
              0.8,
              0.9
            ]

        """

        metrics=defaultdict(list)


        for record in self.records:

            scores=record.get(
                "metrics",
                {}
            )

            for name,value in scores.items():

                metrics[name].append(
                    value
                )


        return dict(metrics)



    def learning_summary(self):

        """
        Produce learning report.
        """

        return {

            "evaluations_seen":
                len(self.records),

            "common_failures":
                self.failure_patterns(),

            "metric_history":
                self.metric_trends()

        }



    def recommend_focus(
        self
    ):
        """
        Suggest what evaluator
        should improve next.
        """

        failures=self.failure_patterns()


        if not failures:
            return "No recurring failures detected."


        worst=max(
            failures,
            key=failures.get
        )


        return (
            f"Focus improvement on: {worst}"
        )