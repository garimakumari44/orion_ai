from __future__ import annotations

from app.planning.models.planning_template import (
    PlanningTemplate,
    PlanningStage,
    PlanningTask,
)


VALUATION_ANALYSIS_TEMPLATE = PlanningTemplate(
    name="valuation_analysis",
    description="Intrinsic valuation and investment value assessment.",
    stages=[
        PlanningStage(
            name="Data Collection",
            tasks=[
                PlanningTask("Retrieve company financial statements"),
                PlanningTask("Retrieve market price"),
                PlanningTask("Retrieve analyst estimates"),
                PlanningTask("Retrieve industry valuation multiples"),
            ],
        ),
        PlanningStage(
            name="Financial Modeling",
            tasks=[
                PlanningTask("Normalize financial statements"),
                PlanningTask("Forecast revenue"),
                PlanningTask("Forecast earnings"),
                PlanningTask("Forecast cash flows"),
            ],
        ),
        PlanningStage(
            name="Valuation",
            tasks=[
                PlanningTask("Perform DCF valuation"),
                PlanningTask("Perform Comparable Company valuation"),
                PlanningTask("Perform Precedent Transaction valuation"),
                PlanningTask("Estimate intrinsic value"),
            ],
        ),
        PlanningStage(
            name="Risk Analysis",
            tasks=[
                PlanningTask("Perform sensitivity analysis"),
                PlanningTask("Evaluate downside scenarios"),
                PlanningTask("Assess valuation assumptions"),
            ],
        ),
        PlanningStage(
            name="Report",
            tasks=[
                PlanningTask("Generate valuation summary"),
                PlanningTask("Generate investment recommendation"),
            ],
        ),
    ],
)