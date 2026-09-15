from __future__ import annotations

from typing import Optional, Any

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

    Canonical architecture:

        Raw Query
            |
            v
        PlanningParser
            |
            v
        PlanningRequest
            |
            v
        Planner
            |
            v
        Task[]
            |
            v
        GraphBuilder
            |
            v
        TaskGraph
            |
            v
        GraphValidator
            |
            v
        Scheduler
            |
            v
        ExecutionPlanBuilder
            |
            v
        ExecutionPlan

    LLM architecture:

        PlannerService
              |
              v
        canonical LLMManager
              |
              +--> ContextBudget
              +--> ModelRouter
              +--> ProviderRouter
              +--> FallbackStrategy
              +--> Provider
    """

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
        parser: Optional[PlanningParser] = None,
        planner: Optional[Planner] = None,
        graph_builder: Optional[GraphBuilder] = None,
        validator: Optional[GraphValidator] = None,
        scheduler: Optional[Scheduler] = None,
        execution_builder: Optional[ExecutionPlanBuilder] = None,
        capability_registry: Optional[Any] = None,
    ) -> None:

        # ==============================================================
        # CANONICAL LLM MANAGER
        # ==============================================================

        if llm_manager is None:
            raise ValueError(
                "PlannerService requires an LLMManager. "
                "Create the canonical LLMManager in the application "
                "composition root and inject it into PlannerService."
            )

        self.llm_manager = llm_manager

        # ==============================================================
        # PARSER
        # ==============================================================

        self.parser = (
            parser
            or PlanningParser(self.llm_manager)
        )

        # ==============================================================
        # PLANNER
        # ==============================================================

        self.planner = (
            planner
            or Planner(
                llm_manager=self.llm_manager,
                capability_registry=capability_registry,
            )
        )

        # ==============================================================
        # GRAPH PIPELINE
        # ==============================================================

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

        # ==============================================================
        # EXECUTION PLAN BUILDER
        # ==============================================================

        self.execution_builder = (
            execution_builder
            or ExecutionPlanBuilder(
                llm_manager=self.llm_manager
            )
        )

    # ==================================================================
    # CREATE PLAN
    # ==================================================================

    def create_plan(
        self,
        query: str,
    ) -> ExecutionPlan:
        """
        Execute the complete planning pipeline.

        Parameters
        ----------
        query:
            Raw user query.

        Returns
        -------
        ExecutionPlan
            Validated and scheduled execution plan.
        """

        if query is None:
            raise ValueError(
                "Planning query cannot be None."
            )

        query = str(query).strip()

        if not query:
            raise ValueError(
                "Planning query cannot be empty."
            )

        # --------------------------------------------------------------
        # Step 1: Parse raw query
        # --------------------------------------------------------------

        planning_request = self.parser.parse(
            query
        )

        # --------------------------------------------------------------
        # Step 2: Generate logical tasks
        # --------------------------------------------------------------

        tasks = self.planner.create_plan(
            planning_request
        )

        if not tasks:
            raise ValueError(
                "Planner produced no executable tasks."
            )

        # --------------------------------------------------------------
        # Step 3: Build dependency graph
        # --------------------------------------------------------------

        graph = self.graph_builder.build(
            tasks
        )

        # --------------------------------------------------------------
        # Step 4: Validate graph
        # --------------------------------------------------------------

        self.validator.validate(
            graph
        )

        # --------------------------------------------------------------
        # Step 5: Schedule execution
        # --------------------------------------------------------------

        execution_order = self.scheduler.schedule(
            graph
        )

        # --------------------------------------------------------------
        # Step 6: Build final execution plan
        # --------------------------------------------------------------

        execution_plan = (
            self.execution_builder.build(
                graph=graph,
                execution_order=execution_order,
            )
        )

        return execution_plan
