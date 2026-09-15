"""
AI Quality Dashboard

Tracks intelligence quality metrics:
- Accuracy
- Hallucinations
- Retrieval performance
- Agent behavior
"""


from dataclasses import dataclass, field
from typing import List, Dict



@dataclass
class QualityPanel:

    name: str
    metric: str
    visualization: str
    description: str



@dataclass
class AIQualityDashboard:

    name: str = "AI Quality Monitoring"

    panels: List[QualityPanel] = field(default_factory=list)



    def __post_init__(self):

        self.panels = [

            QualityPanel(
                name="Response Accuracy",
                metric="answer_accuracy",
                visualization="score",
                description=
                "Measures correctness of AI responses"
            ),


            QualityPanel(
                name="Hallucination Rate",
                metric="hallucination_rate",
                visualization="percentage",
                description=
                "Tracks unsupported AI generated claims"
            ),


            QualityPanel(
                name="Citation Quality",
                metric="citation_accuracy",
                visualization="score",
                description=
                "Measures source grounding quality"
            ),


            QualityPanel(
                name="Retrieval Precision",
                metric="retrieval_precision",
                visualization="score",
                description=
                "Quality of retrieved documents"
            ),


            QualityPanel(
                name="Context Relevance",
                metric="context_relevance",
                visualization="score",
                description=
                "Measures usefulness of retrieved context"
            ),


            QualityPanel(
                name="Agent Success Rate",
                metric="agent_success_rate",
                visualization="percentage",
                description=
                "Successful task completion by agents"
            ),


            QualityPanel(
                name="Tool Usage Accuracy",
                metric="tool_execution_accuracy",
                visualization="score",
                description=
                "Correctness of tool selection and execution"
            ),


            QualityPanel(
                name="User Feedback Score",
                metric="user_rating",
                visualization="rating",
                description=
                "Human evaluation score"
            ),

        ]


    def get_panels(self):

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



ai_quality_dashboard = AIQualityDashboard()