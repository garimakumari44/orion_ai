from __future__ import annotations

from app.planning.models.planning_template import (
    PlanningTemplate,
    PlanningStage,
    PlanningTask,
)


INVESTMENT_MEMO_TEMPLATE = PlanningTemplate(
    name="investment_memo",
    description="Professional investment memorandum for equity research.",
    stages=[
        PlanningStage(
            name="Executive Summary",
            tasks=[
                PlanningTask("Summarize investment thesis"),
                PlanningTask("Summarize company overview"),
            ],
        ),
        PlanningStage(
            name="Business Analysis",
            tasks=[
                PlanningTask("Summarize business model"),
                PlanningTask("Summarize competitive advantages"),
                PlanningTask("Summarize industry outlook"),
            ],
        ),
        PlanningStage(
            name="Financial Analysis",
            tasks=[
                PlanningTask("Summarize financial performance"),
                PlanningTask("Summarize valuation"),
                PlanningTask("Summarize growth expectations"),
            ],
        ),
        PlanningStage(
            name="Investment Assessment",
            tasks=[
                PlanningTask("Summarize investment risks"),
                PlanningTask("Summarize catalysts"),
                PlanningTask("Determine conviction level"),
            ],
        ),
        PlanningStage(
            name="Recommendation",
            tasks=[
                PlanningTask("Generate investment recommendation"),
                PlanningTask("Generate target price rationale"),
                PlanningTask("Generate final investment memo"),
            ],
        ),
    ],
)