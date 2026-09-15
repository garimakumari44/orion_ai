"""
Planner Critic.

Validates execution plans before they are executed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PlanTask:
    id: str
    name: str
    task_type: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class PlanValidationReport:
    valid: bool
    score: float
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]


class PlannerCritic:
    """
    Performs static validation of an execution plan.
    """

    def critique(self, tasks: List[PlanTask]) -> PlanValidationReport:

        issues = []
        warnings = []
        recommendations = []

        if not tasks:
            issues.append("Execution plan is empty.")

        ids = {task.id for task in tasks}

        # Missing dependency check
        for task in tasks:
            for dep in task.dependencies:
                if dep not in ids:
                    issues.append(
                        f"Task '{task.id}' depends on unknown task '{dep}'."
                    )

        # Duplicate IDs
        if len(ids) != len(tasks):
            issues.append("Duplicate task IDs detected.")

        # Isolated tasks
        for task in tasks:
            if not task.dependencies and len(tasks) > 1:
                warnings.append(
                    f"Task '{task.id}' has no dependencies."
                )

        # Plan size
        if len(tasks) > 100:
            warnings.append(
                "Execution plan is unusually large."
            )

        if not issues:
            recommendations.append(
                "Execution plan passed validation."
            )

        score = max(
            0.0,
            1.0 - (len(issues) * 0.25 + len(warnings) * 0.05),
        )

        return PlanValidationReport(
            valid=len(issues) == 0,
            score=score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
        )