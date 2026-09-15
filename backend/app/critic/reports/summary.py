from datetime import datetime



class ReportGenerator:
    """
    Generates human readable evaluation reports.
    """

    def __init__(
        self,
        metrics: dict,
        issues=None
    ):

        self.metrics = metrics
        self.issues = issues or []



    def status(self):

        score = self.metrics.get(
            "average_score",
            0
        )

        if score >= 0.8:
            return "PASSED"

        elif score >= 0.5:
            return "WARNING"

        return "FAILED"



    def generate(self):

        lines = []

        lines.append(
            "Evaluation Summary"
        )

        lines.append(
            "=" * 40
        )


        lines.append(
            f"Generated: {datetime.utcnow()}"
        )


        lines.append("")


        score = self.metrics.get(
            "average_score",
            0
        )


        lines.append(
            f"Overall Score: {score*100:.1f}%"
        )


        lines.append(
            f"Status: {self.status()}"
        )


        lines.append("")


        lines.append(
            "Evaluator Scores:"
        )


        evaluator_scores = self.metrics.get(
            "evaluators",
            {}
        )


        for name,score in evaluator_scores.items():

            icon = (
                "✓"
                if score >=0.7
                else "✗"
            )

            lines.append(
                f"{icon} {name}: {score*100:.1f}%"
            )


        lines.append("")


        lines.append(
            "Failure Statistics:"
        )


        lines.append(
            f"Pass Rate: "
            f"{self.metrics.get('pass_rate',0)*100:.1f}%"
        )


        lines.append(
            f"Failure Rate: "
            f"{self.metrics.get('failure_rate',0)*100:.1f}%"
        )


        lines.append("")


        if self.issues:

            lines.append(
                "Issues:"
            )

            for issue in self.issues:

                lines.append(
                    f"- {issue}"
                )


        return "\n".join(lines)