"""
Weekly Observability Report Generator

Aggregates daily reports and produces:
- trends
- averages
- system health score
- recommendations
"""


from datetime import datetime, timezone
from typing import List, Dict, Any


class WeeklyReport:
    """
    Creates weekly AI system reports.
    """


    def __init__(self):

        self.created_at = datetime.now(
            timezone.utc
        )


    def generate(
        self,
        daily_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate weekly report
        from daily reports.
        """


        if not daily_reports:
            return {
                "error": "No reports available"
            }


        total_requests = sum(
            r["performance"]["requests"]
            for r in daily_reports
        )


        avg_latency = (
            sum(
                r["performance"]["latency"]
                for r in daily_reports
            )
            /
            len(daily_reports)
        )


        avg_success = (
            sum(
                r["reliability"]["success_rate"]
                for r in daily_reports
            )
            /
            len(daily_reports)
        )


        total_cost = sum(
            r["cost"]["total_cost"]
            for r in daily_reports
        )


        return {

            "report_type": "weekly",

            "period": {
                "start":
                    daily_reports[0]["date"],

                "end":
                    daily_reports[-1]["date"]
            },


            "traffic": {

                "total_requests":
                    total_requests
            },


            "performance": {

                "average_latency":
                    round(
                        avg_latency,
                        3
                    )
            },


            "reliability": {

                "average_success_rate":
                    round(
                        avg_success,
                        4
                    )
            },


            "cost": {

                "total_cost":
                    round(
                        total_cost,
                        2
                    )
            },


            "health_score":
                self._health_score(
                    avg_success,
                    avg_latency
                ),


            "recommendations":
                self._recommendations(
                    avg_success,
                    avg_latency
                ),


            "generated_at":
                self.created_at.isoformat()
        }



    def _health_score(
        self,
        success_rate: float,
        latency: float
    ) -> float:

        score = (
            success_rate * 100
        )


        if latency > 3:
            score -= 10


        return round(
            max(score,0),
            2
        )



    def _recommendations(
        self,
        success_rate,
        latency
    ):

        recommendations = []


        if latency > 3:

            recommendations.append(
                "Optimize slow AI pipelines"
            )


        if success_rate < 0.95:

            recommendations.append(
                "Investigate failed requests"
            )


        if not recommendations:

            recommendations.append(
                "System performance is healthy"
            )


        return recommendations