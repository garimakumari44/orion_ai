"""
Performance Report Generator

Analyzes AI system performance:
- latency
- throughput
- token efficiency
- model response quality
- infrastructure bottlenecks
"""


from datetime import datetime, timezone
from typing import Dict, Any, List



class PerformanceReport:
    """
    Generates engineering performance reports.
    """


    def __init__(self):

        self.generated_at = datetime.now(
            timezone.utc
        )



    def generate(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate performance report.

        Example:

        {
            "latency": {
                "p50": 0.8,
                "p95": 2.5,
                "p99": 5
            },

            "requests": 50000,

            "tokens": {
                "input": 1000000,
                "output": 300000
            },

            "models": {
                "gpt": {
                    "latency": 1.2
                }
            }
        }

        """


        return {

            "report_type":
                "performance",


            "latency":
                self._latency_analysis(
                    metrics.get(
                        "latency",
                        {}
                    )
                ),


            "throughput":
                self._throughput_analysis(
                    metrics
                ),


            "token_efficiency":
                self._token_analysis(
                    metrics.get(
                        "tokens",
                        {}
                    )
                ),


            "model_analysis":
                self._model_analysis(
                    metrics.get(
                        "models",
                        {}
                    )
                ),


            "bottlenecks":
                self._detect_bottlenecks(
                    metrics
                ),


            "generated_at":
                self.generated_at.isoformat()
        }



    def _latency_analysis(
        self,
        latency: Dict[str,float]
    ):

        return {

            "p50":
                latency.get(
                    "p50",
                    0
                ),

            "p95":
                latency.get(
                    "p95",
                    0
                ),

            "p99":
                latency.get(
                    "p99",
                    0
                ),


            "status":
                (
                    "healthy"
                    if latency.get(
                        "p95",
                        0
                    ) < 3
                    else
                    "slow"
                )
        }



    def _throughput_analysis(
        self,
        metrics
    ):

        requests = metrics.get(
            "requests",
            0
        )

        duration = metrics.get(
            "duration",
            1
        )


        return {

            "requests":
                requests,


            "requests_per_second":
                round(
                    requests / duration,
                    2
                )
        }



    def _token_analysis(
        self,
        tokens
    ):

        input_tokens = tokens.get(
            "input",
            0
        )

        output_tokens = tokens.get(
            "output",
            0
        )


        return {

            "input_tokens":
                input_tokens,


            "output_tokens":
                output_tokens,


            "total_tokens":
                input_tokens +
                output_tokens,


            "output_ratio":
                round(
                    output_tokens /
                    max(input_tokens,1),
                    3
                )
        }



    def _model_analysis(
        self,
        models
    ):

        result = []


        for name,data in models.items():

            result.append({

                "model":
                    name,

                "latency":
                    data.get(
                        "latency",
                        0
                    ),

                "errors":
                    data.get(
                        "errors",
                        0
                    )
            })


        return result



    def _detect_bottlenecks(
        self,
        metrics
    ) -> List[str]:


        issues = []


        if metrics.get(
            "latency",
            {}
        ).get(
            "p95",
            0
        ) > 3:

            issues.append(
                "High inference latency"
            )


        if metrics.get(
            "cpu_usage",
            0
        ) > 90:

            issues.append(
                "CPU saturation"
            )


        if metrics.get(
            "memory_usage",
            0
        ) > 90:

            issues.append(
                "Memory pressure"
            )


        return issues