"""
Engineering Dashboard

Tracks technical health of AI systems:
- Latency
- Throughput
- Errors
- Infrastructure
- Model execution performance
"""


from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class DashboardPanel:
    name: str
    metric: str
    visualization: str
    description: str


@dataclass
class EngineeringDashboard:
    """
    Engineering observability dashboard definition.
    """

    name: str = "Engineering Health"

    panels: List[DashboardPanel] = field(default_factory=list)


    def __post_init__(self):

        self.panels = [

            DashboardPanel(
                name="API Latency",
                metric="request_latency_ms",
                visualization="timeseries",
                description=
                "Tracks API response latency over time"
            ),


            DashboardPanel(
                name="LLM Latency",
                metric="llm_latency_ms",
                visualization="timeseries",
                description=
                "Measures model inference latency"
            ),


            DashboardPanel(
                name="Request Throughput",
                metric="requests_per_second",
                visualization="graph",
                description=
                "Number of requests processed per second"
            ),


            DashboardPanel(
                name="Error Rate",
                metric="error_rate",
                visualization="percentage",
                description=
                "Application and service failure percentage"
            ),


            DashboardPanel(
                name="Token Usage",
                metric="tokens_consumed",
                visualization="counter",
                description=
                "Tracks prompt and completion token consumption"
            ),


            DashboardPanel(
                name="Infrastructure CPU",
                metric="cpu_usage",
                visualization="gauge",
                description=
                "CPU utilization across services"
            ),


            DashboardPanel(
                name="Memory Usage",
                metric="memory_usage",
                visualization="gauge",
                description=
                "RAM consumption by services"
            ),


            DashboardPanel(
                name="Active Traces",
                metric="trace_count",
                visualization="counter",
                description=
                "Distributed tracing activity"
            ),

        ]


    def get_panels(self) -> List[Dict]:
        """
        Export dashboard panels.
        """

        return [
            {
                "name": panel.name,
                "metric": panel.metric,
                "visualization": panel.visualization,
                "description": panel.description
            }
            for panel in self.panels
        ]


    def get_metrics(self):
        """
        Returns all tracked metrics.
        """

        return [
            panel.metric
            for panel in self.panels
        ]


engineering_dashboard = EngineeringDashboard()