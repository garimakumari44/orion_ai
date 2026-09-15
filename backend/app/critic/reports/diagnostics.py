from typing import List, Dict, Any
from datetime import datetime


class DiagnosticAnalyzer:
    """
    Generates detailed diagnostics from evaluation results.
    """

    def __init__(
        self,
        results: List[Dict[str, Any]]
    ):

        self.results = results


    def failed_checks(self):

        failures = []

        for result in self.results:

            if not result.get("passed", False):

                failures.append({

                    "evaluator":
                        result.get(
                            "name",
                            "unknown"
                        ),

                    "score":
                        result.get(
                            "score",
                            0
                        ),

                    "severity":
                        result.get(
                            "severity",
                            "unknown"
                        ),

                    "reason":
                        result.get(
                            "reason",
                            "No reason provided"
                        )
                })


        return failures



    def weak_areas(
        self,
        threshold: float = 0.7
    ):

        """
        Finds evaluators with low scores.
        """

        weak = []


        for result in self.results:

            score = result.get(
                "score",
                0
            )


            if score < threshold:

                weak.append({

                    "area":
                        result.get(
                            "name"
                        ),

                    "score":
                        score

                })


        return weak



    def recommendations(self):

        recommendations = []


        for failure in self.failed_checks():

            evaluator = failure["evaluator"]


            if evaluator == "factual":

                recommendations.append(
                    "Run retrieval verification and fact checking."
                )


            elif evaluator == "citation":

                recommendations.append(
                    "Validate sources and repair missing citations."
                )


            elif evaluator == "logic":

                recommendations.append(
                    "Regenerate reasoning chain."
                )


            else:

                recommendations.append(
                    f"Review {evaluator} evaluator."
                )


        return list(set(recommendations))



    def generate(self):

        return {

            "timestamp":
                datetime.utcnow().isoformat(),


            "total_checks":
                len(self.results),


            "failed_checks":
                self.failed_checks(),


            "weak_areas":
                self.weak_areas(),


            "recommendations":
                self.recommendations()

        }