"""
Daily Observability Report Generator

Generates daily summaries from:
- latency metrics
- failures
- token usage
- cost
- resource usage
- AI quality metrics
"""

from datetime import datetime, timezone
from typing import Dict, Any, List


class DailyReport:
    """
    Creates daily operational reports.
    """

    def __init__(self):
        self.report_date = datetime.now(timezone.utc).date()

    def generate(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate daily report.

        Example metrics:
        {
            "requests": 5000,
            "success_rate": 0.98,
            "avg_latency": 1.4,
            "tokens": 250000,
            "cost": 12.50,
            "errors": 50
        }
        """

        report = {
            "report_type": "daily",
            "date": str(self.report_date),

            "summary": self._summary(metrics),

            "performance": {
                "requests": metrics.get(
                    "requests",
                    0
                ),

                "latency": metrics.get(
                    "avg_latency",
                    0
                ),

                "throughput": metrics.get(
                    "throughput",
                    0
                )
            },

            "reliability": {
                "success_rate": metrics.get(
                    "success_rate",
                    0
                ),

                "failures": metrics.get(
                    "errors",
                    0
                )
            },


            "cost": {
                "tokens": metrics.get(
                    "tokens",
                    0
                ),

                "total_cost": metrics.get(
                    "cost",
                    0
                )
            },


            "alerts": self._generate_alerts(metrics),

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }


        return report


    def _summary(
        self,
        metrics: Dict[str, Any]
    ) -> str:

        success = metrics.get(
            "success_rate",
            0
        )

        latency = metrics.get(
            "avg_latency",
            0
        )


        return (
            f"System processed "
            f"{metrics.get('requests',0)} requests. "
            f"Success rate {success*100:.2f}%. "
            f"Average latency {latency}s."
        )


    def _generate_alerts(
        self,
        metrics: Dict[str, Any]
    ) -> List[str]:

        alerts = []


        if metrics.get(
            "avg_latency",
            0
        ) > 3:

            alerts.append(
                "High latency detected"
            )


        if metrics.get(
            "success_rate",
            1
        ) < 0.95:

            alerts.append(
                "Failure rate above threshold"
            )


        if metrics.get(
            "cost",
            0
        ) > 100:

            alerts.append(
                "High inference cost"
            )


        return alerts