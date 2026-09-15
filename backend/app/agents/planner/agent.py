"""
Planner Agent

Responsible for transforming investor questions
into research workflows.
"""


from .models import (
    ResearchRequest,
    ResearchObjective,
    PlannerResponse,
    PlannerTask
)

from .research_planner import ResearchPlanner
from .task_decomposer import TaskDecomposer
from .priority import PriorityManager


class PlannerAgent:
    """
    Main Planner Agent.
    """

    def __init__(self):
        self.research_planner = ResearchPlanner()
        self.task_decomposer = TaskDecomposer()
        self.priority_manager = PriorityManager()


    async def plan(
        self,
        request: ResearchRequest
    ) -> PlannerResponse:
        """
        Create research plan.
        """

        objective = (
            await self.research_planner.create_strategy(
                request
            )
        )


        tasks = (
            await self.task_decomposer.create_tasks(
                objective
            )
        )


        tasks = (
            self.priority_manager.assign_priority(
                tasks
            )
        )


        return PlannerResponse(
            objective=objective,
            tasks=tasks,
            metadata={
                "agent": "planner",
                "type": "equity_research"
            }
        )