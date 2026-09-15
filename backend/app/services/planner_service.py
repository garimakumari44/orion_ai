from __future__ import annotations

from typing import Optional

from app.llm.manager import LLMManager
from app.planning.parser import PlanningParser
from app.planning.planner import Planner
from app.planning.graph_builder import GraphBuilder
from app.planning.validator import GraphValidator
from app.planning.scheduler import Scheduler
from app.planning.execution_plan_builder import ExecutionPlanBuilder

from app.planning.models.execution_plan import ExecutionPlan


class PlannerService:
    """
    Coordinates the complete planning pipeline.

    Canonical dependency flow:

        LLMManager
             |
             +--> PlanningParser
             |
             +--> IntentClassifier
             |
             +--> Planner
             |
             +--> ExecutionPlanBuilder
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        parser: Optional[PlanningParser] = None,
        planner: Optional[Planner] = None,
        graph_builder: Optional[GraphBuilder] = None,
        validator: Optional[GraphValidator] = None,
        scheduler: Optional[Scheduler] = None,
        execution_builder: Optional[ExecutionPlanBuilder] = None,
    ) -> None:

        if llm_manager is None:
            raise ValueError(
                "PlannerService requires an LLMManager."
            )

        self.llm_manager = llm_manager

        self.parser = (
            parser
            or PlanningParser(
                llm_manager=self.llm_manager
            )
        )

        self.planner = (
            planner
            or Planner(
                llm_manager=self.llm_manager
            )
        )

        self.graph_builder = (
            graph_builder
            or GraphBuilder()
        )

        self.validator = (
            validator
            or GraphValidator()
        )

        self.scheduler = (
            scheduler
            or Scheduler()
        )

        self.execution_builder = (
            execution_builder
            or ExecutionPlanBuilder(
                llm_manager=self.llm_manager
            )
        )

    def create_plan(
        self,
        query: str,
    ) -> ExecutionPlan:
        """
        Execute the complete planning pipeline.
        """

        planning_request = self.parser.parse(query)

        tasks = self.planner.create_plan(
            planning_request
        )

        graph = self.graph_builder.build(tasks)

        self.validator.validate(graph)

        execution_order = self.scheduler.schedule(
            graph
        )

        return self.execution_builder.build(
            graph=graph,
            execution_order=execution_order,
        )
