"""
Business Dashboard

Tracks business impact of AI systems:

- User adoption
- Customer engagement
- Revenue impact
- Cost efficiency
- Product value
"""


from dataclasses import dataclass, field
from typing import List, Dict



@dataclass
class BusinessPanel:

    name: str
    metric: str
    visualization: str
    description: str



@dataclass
class BusinessDashboard:

    name: str = "Business Impact"

    panels: List[BusinessPanel] = field(default_factory=list)



    def __post_init__(self):

        self.panels = [

            BusinessPanel(
                name="Active Users",
                metric="daily_active_users",
                visualization="counter",
                description=
                "Number of active users interacting with AI system"
            ),


            BusinessPanel(
                name="Conversation Volume",
                metric="conversation_count",
                visualization="timeseries",
                description=
                "Total AI conversations handled"
            ),


            BusinessPanel(
                name="User Engagement",
                metric="engagement_rate",
                visualization="percentage",
                description=
                "Measures user interaction quality"
            ),


            BusinessPanel(
                name="Task Completion Rate",
                metric="task_success_rate",
                visualization="percentage",
                description=
                "Percentage of successfully completed tasks"
            ),


            BusinessPanel(
                name="Customer Satisfaction",
                metric="customer_satisfaction_score",
                visualization="score",
                description=
                "User satisfaction rating"
            ),


            BusinessPanel(
                name="AI Cost Per Request",
                metric="cost_per_request",
                visualization="currency",
                description=
                "Average AI infrastructure cost per request"
            ),


            BusinessPanel(
                name="Revenue Impact",
                metric="revenue_generated",
                visualization="currency",
                description=
                "Revenue attributed to AI workflows"
            ),


            BusinessPanel(
                name="ROI",
                metric="ai_roi",
                visualization="percentage",
                description=
                "Return on AI investment"
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



business_dashboard = BusinessDashboard()