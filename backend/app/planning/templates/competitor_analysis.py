from __future__ import annotations

from app.planning.models.planning_template import (
    PlanningTemplate,
    PlanningStage,
    PlanningTask,
)


COMPETITOR_ANALYSIS_TEMPLATE = PlanningTemplate(
    name="competitor_analysis",
    description="Comprehensive competitive intelligence and benchmarking.",
    stages=[
        PlanningStage(
            name="Competitor Identification",
            tasks=[
                PlanningTask("Identify direct competitors"),
                PlanningTask("Identify indirect competitors"),
                PlanningTask("Identify emerging competitors"),
                PlanningTask("Categorize competitors"),
            ],
        ),
        PlanningStage(
            name="Business Comparison",
            tasks=[
                PlanningTask("Compare products and services"),
                PlanningTask("Compare pricing strategies"),
                PlanningTask("Compare customer segments"),
                PlanningTask("Compare geographic presence"),
            ],
        ),
        PlanningStage(
            name="Financial Benchmarking",
            tasks=[
                PlanningTask("Compare revenue growth"),
                PlanningTask("Compare profitability"),
                PlanningTask("Compare valuation multiples"),
                PlanningTask("Compare capital allocation"),
            ],
        ),
        PlanningStage(
            name="Competitive Positioning",
            tasks=[
                PlanningTask("Perform SWOT comparison"),
                PlanningTask("Identify competitive advantages"),
                PlanningTask("Identify competitive weaknesses"),
                PlanningTask("Assess market positioning"),
            ],
        ),
        PlanningStage(
            name="Summary",
            tasks=[
                PlanningTask("Generate competitive insights"),
                PlanningTask("Generate strategic recommendations"),
            ],
        ),
    ],
)