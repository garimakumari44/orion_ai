"""
Operations Dashboard

Tracks production operations:

- Availability
- Reliability
- Incidents
- Deployments
- Dependencies
"""


from dataclasses import dataclass, field
from typing import List, Dict



@dataclass
class OperationsPanel:

    name: str
    metric: str
    visualization: str
    description: str



@dataclass
class OperationsDashboard:

    name: str = "Operations Health"

    panels: List[OperationsPanel] = field(default_factory=list)



    def __post_init__(self):

        self.panels = [

            OperationsPanel(
                name="System Availability",
                metric="uptime_percentage",
                visualization="percentage",
                description=
                "Overall system uptime"
            ),


            OperationsPanel(
                name="Service Health",
                metric="service_health_status",
                visualization="status",
                description=
                "Health status of all services"
            ),


            OperationsPanel(
                name="Incident Count",
                metric="incident_count",
                visualization="counter",
                description=
                "Production incidents detected"
            ),


            OperationsPanel(
                name="Mean Time To Recovery",
                metric="mttr",
                visualization="duration",
                description=
                "Average recovery time after failures"
            ),


            OperationsPanel(
                name="Deployment Frequency",
                metric="deployment_frequency",
                visualization="timeseries",
                description=
                "Frequency of production deployments"
            ),


            OperationsPanel(
                name="Deployment Failures",
                metric="deployment_failure_rate",
                visualization="percentage",
                description=
                "Failed production deployments"
            ),


            OperationsPanel(
                name="Dependency Status",
                metric="dependency_health",
                visualization="status",
                description=
                "External API and service health"
            ),


            OperationsPanel(
                name="Queue Health",
                metric="queue_latency",
                visualization="timeseries",
                description=
                "Background processing queue performance"
            ),


            OperationsPanel(
                name="Worker Status",
                metric="active_workers",
                visualization="counter",
                description=
                "Number of active execution workers"
            ),

        ]



    def get_panels(self) -> List[Dict]:

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

        return [
            panel.metric
            for panel in self.panels
        ]



operations_dashboard = OperationsDashboard()