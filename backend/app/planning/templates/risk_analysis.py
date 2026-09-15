from __future__ import annotations

from app.planning.models.planning_template import (
    PlanningTemplate,
    PlanningStage,
    PlanningTask,
)


RISK_ANALYSIS_TEMPLATE = PlanningTemplate(
    name="risk_analysis",
    description="Enterprise investment risk assessment.",
    stages=[
        PlanningStage(
            name="Business Risk",
            tasks=[
                PlanningTask("Analyze business model risks"),
                PlanningTask("Analyze operational risks"),
                PlanningTask("Analyze execution risks"),
            ],
        ),
        PlanningStage(
            name="Financial Risk",
            tasks=[
                PlanningTask("Analyze liquidity"),
                PlanningTask("Analyze leverage"),
                PlanningTask("Analyze cash flow stability"),
                PlanningTask("Analyze credit risk"),
            ],
        ),
        PlanningStage(
            name="External Risk",
            tasks=[
                PlanningTask("Analyze macroeconomic risks"),
                PlanningTask("Analyze regulatory risks"),
                PlanningTask("Analyze geopolitical risks"),
                PlanningTask("Analyze industry risks"),
            ],
        ),
        PlanningStage(
            name="Scenario Analysis",
            tasks=[
                PlanningTask("Evaluate bull case"),
                PlanningTask("Evaluate base case"),
                PlanningTask("Evaluate bear case"),
                PlanningTask("Perform sensitivity analysis"),
            ],
        ),
        PlanningStage(
            name="Risk Report",
            tasks=[
                PlanningTask("Rank key risks"),
                PlanningTask("Generate mitigation recommendations"),
            ],
        ),
    ],
)