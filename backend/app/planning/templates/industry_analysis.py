from __future__ import annotations

from app.planning.models.planning_template import (
    PlanningTemplate,
    PlanningStage,
    PlanningTask,
)


INDUSTRY_ANALYSIS_TEMPLATE = PlanningTemplate(
    name="industry_analysis",
    description="Industry structure, trends, competition, and outlook.",
    stages=[
        PlanningStage(
            name="Industry Overview",
            tasks=[
                PlanningTask("Identify industry"),
                PlanningTask("Retrieve industry statistics"),
                PlanningTask("Retrieve market size"),
                PlanningTask("Retrieve market growth"),
            ],
        ),
        PlanningStage(
            name="Competitive Landscape",
            tasks=[
                PlanningTask("Identify competitors"),
                PlanningTask("Compare market share"),
                PlanningTask("Compare business models"),
                PlanningTask("Analyze competitive positioning"),
            ],
        ),
        PlanningStage(
            name="Industry Drivers",
            tasks=[
                PlanningTask("Analyze growth drivers"),
                PlanningTask("Analyze macroeconomic factors"),
                PlanningTask("Analyze regulatory environment"),
                PlanningTask("Analyze technological trends"),
            ],
        ),
        PlanningStage(
            name="Risk Assessment",
            tasks=[
                PlanningTask("Identify industry risks"),
                PlanningTask("Identify disruptive threats"),
                PlanningTask("Assess cyclicality"),
            ],
        ),
        PlanningStage(
            name="Outlook",
            tasks=[
                PlanningTask("Forecast industry outlook"),
                PlanningTask("Generate strategic insights"),
            ],
        ),
    ],
)