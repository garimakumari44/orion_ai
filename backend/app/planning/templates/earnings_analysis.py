from __future__ import annotations

from app.planning.models.planning_template import (
    PlanningTemplate,
    PlanningStage,
    PlanningTask,
)


EARNINGS_ANALYSIS_TEMPLATE = PlanningTemplate(
    name="earnings_analysis",
    description="Comprehensive earnings report analysis.",
    stages=[
        PlanningStage(
            name="Retrieve Earnings",
            tasks=[
                PlanningTask("Retrieve latest earnings report"),
                PlanningTask("Retrieve previous earnings"),
                PlanningTask("Retrieve analyst expectations"),
                PlanningTask("Retrieve earnings call transcript"),
            ],
        ),
        PlanningStage(
            name="Performance Analysis",
            tasks=[
                PlanningTask("Analyze revenue growth"),
                PlanningTask("Analyze earnings growth"),
                PlanningTask("Analyze profitability"),
                PlanningTask("Analyze margins"),
                PlanningTask("Analyze cash flow"),
            ],
        ),
        PlanningStage(
            name="Management Commentary",
            tasks=[
                PlanningTask("Summarize management guidance"),
                PlanningTask("Identify strategic initiatives"),
                PlanningTask("Identify operational risks"),
            ],
        ),
        PlanningStage(
            name="Market Reaction",
            tasks=[
                PlanningTask("Analyze analyst revisions"),
                PlanningTask("Analyze stock price reaction"),
                PlanningTask("Compare expectations vs results"),
            ],
        ),
        PlanningStage(
            name="Summary",
            tasks=[
                PlanningTask("Generate earnings insights"),
                PlanningTask("Generate investment implications"),
            ],
        ),
    ],
)