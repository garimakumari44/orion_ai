from typing import List, Dict


class MetricsCalculator:
    """
    Calculates evaluation metrics from evaluator outputs.
    """

    def __init__(self, results: List[dict]):
        """
        results example:

        [
            {
                "name": "factual",
                "score": 0.9,
                "passed": True,
                "severity": "low"
            }
        ]
        """

        self.results = results


    def total_evaluations(self) -> int:
        return len(self.results)


    def average_score(self) -> float:

        if not self.results:
            return 0.0

        scores = [
            result.get("score",0)
            for result in self.results
        ]

        return round(
            sum(scores) / len(scores),
            3
        )


    def pass_rate(self) -> float:

        if not self.results:
            return 0.0


        passed = sum(
            1
            for result in self.results
            if result.get("passed")
        )

        return round(
            passed / len(self.results),
            3
        )


    def failure_rate(self) -> float:

        return round(
            1 - self.pass_rate(),
            3
        )


    def severity_distribution(self) -> Dict[str,int]:

        distribution = {}

        for result in self.results:

            severity = result.get(
                "severity",
                "unknown"
            )

            distribution[severity] = (
                distribution.get(severity,0)+1
            )

        return distribution



    def evaluator_scores(self):

        scores = {}

        for result in self.results:

            name = result.get(
                "name",
                "unknown"
            )

            scores[name] = result.get(
                "score",
                0
            )

        return scores



    def generate(self):

        return {

            "total_evaluations":
                self.total_evaluations(),

            "average_score":
                self.average_score(),

            "pass_rate":
                self.pass_rate(),

            "failure_rate":
                self.failure_rate(),

            "severity":
                self.severity_distribution(),

            "evaluators":
                self.evaluator_scores()
        }