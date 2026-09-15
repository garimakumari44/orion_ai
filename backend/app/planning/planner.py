"""
app/planning/planner.py

Main Planning Orchestrator.

Responsibilities
----------------
- Understand planning requests.
- Select the appropriate planning strategy.
- Generate executable tasks.
- Build the execution graph.
- Schedule tasks.
- Create an ExecutionPlan.

Specialized planners
--------------------
- KnowledgePlanner
- ResearchPlanner

LLM architecture
----------------
The planner does NOT construct LLM providers directly.

All LLM calls go through:

    Planner
        |
        v
    LLMManager
        |
        v
    ModelRouter
        |
        v
    ProviderRouter
        |
        v
    Provider

Memory
------
Memory is NOT represented as an executable agent task.

Memory/retrieval is provided through the execution context and
knowledge/retrieval services during execution.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.planning.models.planning_request import PlanningRequest
from app.planning.models.task import (
    Task,
    TaskPriority,
    TaskType,
)
from app.planning.models.execution_plan import ExecutionPlan
from app.planning.models.task_graph import TaskGraph

from app.planning.scheduler import Scheduler
from app.planning.knowledge_planner import KnowledgePlanner

from app.orchestration.capability import Capability
from app.agents.planner.research_planner import ResearchPlanner

from app.llm.manager import LLMManager


logger = logging.getLogger(__name__)


class Planner:
    """
    Main Planning Orchestrator.

    This class is responsible for planning.

    It does NOT own:

    - LLM provider creation
    - provider selection
    - API calls
    - memory storage
    - retrieval implementation

    Those responsibilities belong elsewhere.
    """

    # ==================================================================
    # SUPPORTED INTENTS
    # ==================================================================

    RESEARCH_INTENTS = {
        "company_research",
        "company_comparison",
        "industry_research",
        "earnings_analysis",
        "valuation_analysis",
        "risk_analysis",
        "macro_research",
        "portfolio_research",
        "theme_research",
    }

    KNOWLEDGE_INTENTS = {
        "knowledge_lookup",
        "document_search",
        "entity_lookup",
    }

    # ==================================================================
    # INITIALIZATION
    # ==================================================================

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
        capability_registry: Optional[Any] = None,
    ) -> None:
        """
        Initialize the planner.

        Parameters
        ----------
        llm_manager:
            Canonical LLMManager instance.

            The planner should receive this from the application
            composition root.

        capability_registry:
            Registry containing available capabilities.
        """

        if llm_manager is None:

            raise ValueError(
                "Planner requires an LLMManager. "
                "Create LLMManager in the application "
                "composition root and inject it into Planner."
            )

        self.llm_manager = llm_manager

        self.capability_registry = (
            capability_registry
        )

        # --------------------------------------------------------------
        # Specialized planners
        # --------------------------------------------------------------

        self.knowledge_planner = (
            KnowledgePlanner()
        )

        self.research_planner = (
            ResearchPlanner()
        )

        logger.info(
            "Planner initialized | "
            "knowledge_planner=%s | "
            "research_planner=%s | "
            "llm_manager=%s",
            type(
                self.knowledge_planner
            ).__name__,
            type(
                self.research_planner
            ).__name__,
            type(
                self.llm_manager
            ).__name__,
        )

    # ==================================================================
    # MAIN ENTRY
    # ==================================================================

    def create_plan(
        self,
        request: PlanningRequest,
    ) -> ExecutionPlan:
        """
        Create an execution plan for a planning request.

        Memory is intentionally NOT added as an executable task.

        Retrieval and memory context should be supplied through
        AgentContext / knowledge services during execution.
        """

        if request is None:
            raise ValueError(
                "PlanningRequest cannot be None."
            )

        logger.info(
            "Creating execution plan | intent=%s",
            getattr(
                request,
                "intent",
                None,
            ),
        )

        tasks = self._select_planner(
            request
        )

        if not tasks:
            raise ValueError(
                "Planner produced no executable tasks."
            )

        return self._build_execution_plan(
            request=request,
            tasks=tasks,
        )

    # ==================================================================
    # PLANNER ROUTER
    # ==================================================================

    def _select_planner(
        self,
        request: PlanningRequest,
    ) -> List[Task]:
        """
        Select the appropriate specialized planner.
        """

        intent = (
            getattr(
                request,
                "intent",
                "",
            )
            or ""
        ).strip().lower()

        # --------------------------------------------------------------
        # Research planning
        # --------------------------------------------------------------

        if intent in self.RESEARCH_INTENTS:

            logger.info(
                "Routing request to ResearchPlanner | intent=%s",
                intent,
            )

            return self.research_planner.plan(
                research_type=intent,
                parameters={
                    "query": request.query,
                },
            )

        # --------------------------------------------------------------
        # Knowledge planning
        # --------------------------------------------------------------

        if intent in self.KNOWLEDGE_INTENTS:

            logger.info(
                "Routing request to KnowledgePlanner | intent=%s",
                intent,
            )

            return self.knowledge_planner.plan(
                request
            )

        # --------------------------------------------------------------
        # Generic LLM planning
        # --------------------------------------------------------------

        logger.info(
            "Routing request to LLM planner | intent=%s",
            intent,
        )

        return self._llm_based_plan(
            request
        )

    # ==================================================================
    # LLM PLANNER
    # ==================================================================

    def _llm_based_plan(
        self,
        request: PlanningRequest,
    ) -> List[Task]:
        """
        Generate a task plan using the canonical LLMManager.

        IMPORTANT
        ---------
        This method does NOT instantiate LLMService.

        All LLM operations go through:

            self.llm_manager
        """

        capabilities = (
            self._get_available_capabilities()
        )

        # --------------------------------------------------------------
        # Keep planner context compact.
        #
        # Do not dump unnecessary application state into the prompt.
        # This is important for preventing the large-prompt problem
        # seen in the OpenRouter logs.
        # --------------------------------------------------------------

        capabilities_json = json.dumps(
            capabilities,
            indent=2,
            ensure_ascii=False,
        )

        prompt = f"""
You are an autonomous AI execution planner.

Convert the user request into a small executable DAG.

AVAILABLE CAPABILITIES:
{capabilities_json}

PLANNING RULES:

1. Create only the tasks required to satisfy the request.
2. Every task must have a capability.
3. Tasks must be atomic and executable.
4. Add dependencies where one task requires another.
5. Dependencies must refer to task references or task titles.
6. Do not create memory retrieval tasks.
7. Do not create memory storage tasks.
8. Memory and retrieval context are handled by the execution system.
9. assigned_executor must identify a registered executor when known.
10. task_type must be a supported TaskType value.
11. priority must be a supported TaskPriority value.
12. Avoid duplicate tasks.
13. Keep the number of tasks as small as reasonably possible.
14. Output JSON only.
15. Do not output markdown.
16. Do not output explanations.

USER REQUEST:
{request.query}

REQUEST INTENT:
{request.intent}

RETURN EXACTLY THIS STRUCTURE:

[
    {{
        "title": "short task title",
        "description": "what this task must accomplish",
        "capability": "capability name",
        "assigned_executor": "executor name",
        "dependencies": [],
        "task_type": "EXECUTE",
        "priority": "MEDIUM",
        "parameters": {{}}
    }}
]
"""

        logger.debug(
            "Generating LLM execution plan | intent=%s",
            request.intent,
        )

        # --------------------------------------------------------------
        # CANONICAL LLM ENTRY
        # --------------------------------------------------------------

        response = self.llm_manager.generate(
            prompt=prompt,
            task="planning",
            temperature=0.0,
            max_tokens=1200,
        )

        response = self._normalize_llm_response(
            response
        )

        if not isinstance(
            response,
            list,
        ):

            raise ValueError(
                "LLM planner must return a list of tasks."
            )

        if not response:

            raise ValueError(
                "LLM planner returned an empty task list."
            )

        return self._parse_llm_tasks(
            response
        )

    # ==================================================================
    # LLM RESPONSE NORMALIZATION
    # ==================================================================

    @staticmethod
    def _normalize_llm_response(
        response: Any,
    ) -> Any:
        """
        Normalize an LLM planner response into Python data.

        Handles:

        - plain Python lists
        - JSON strings
        - markdown JSON fences
        """

        if isinstance(
            response,
            list,
        ):
            return response

        if not isinstance(
            response,
            str,
        ):

            raise ValueError(
                "LLM planner returned an unsupported response type."
            )

        text = response.strip()

        if not text:

            raise ValueError(
                "LLM planner returned an empty response."
            )

        # --------------------------------------------------------------
        # Remove markdown fences safely.
        # --------------------------------------------------------------

        if text.startswith("```"):

            lines = text.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(
                lines
            ).strip()

        try:

            return json.loads(
                text
            )

        except json.JSONDecodeError as exc:

            logger.error(
                "Failed to parse LLM planner response: %s",
                text[:1000],
            )

            raise ValueError(
                "LLM planner returned invalid JSON."
            ) from exc

    # ==================================================================
    # CAPABILITY DISCOVERY
    # ==================================================================

    def _get_available_capabilities(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return capabilities available to the planner.
        """

        if self.capability_registry is None:
            return []

        list_method = getattr(
            self.capability_registry,
            "list",
            None,
        )

        if not callable(list_method):
            return []

        capabilities: List[
            Dict[str, Any]
        ] = []

        for capability in list_method():

            capabilities.append(
                {
                    "name": getattr(
                        capability,
                        "name",
                        str(capability),
                    ),
                    "description": getattr(
                        capability,
                        "description",
                        "",
                    ),
                    "source": getattr(
                        capability,
                        "source",
                        "local",
                    ),
                }
            )

        return capabilities

    # ==================================================================
    # LLM TASK PARSER
    # ==================================================================

    def _parse_llm_tasks(
        self,
        items: list,
    ) -> List[Task]:
        """
        Convert LLM-generated task dictionaries into Task objects.
        """

        tasks: List[Task] = []

        task_reference_map: Dict[
            str,
            str,
        ] = {}

        # --------------------------------------------------------------
        # First pass
        #
        # Create stable internal UUIDs.
        # --------------------------------------------------------------

        for item in items:

            if not isinstance(
                item,
                dict,
            ):

                raise ValueError(
                    "Each LLM task must be a JSON object."
                )

            task_id = str(
                uuid.uuid4()
            )

            title = str(
                item.get(
                    "title",
                    "",
                )
            ).strip()

            if not title:

                raise ValueError(
                    "LLM-generated task is missing 'title'."
                )

            # ----------------------------------------------------------
            # Capability is required.
            # ----------------------------------------------------------

            capability = item.get(
                "capability"
            )

            if capability is None:

                raise ValueError(
                    f"LLM-generated task '{title}' "
                    "is missing 'capability'."
                )

            capability = str(
                capability
            ).strip()

            if not capability:

                raise ValueError(
                    f"LLM-generated task '{title}' "
                    "has an empty capability."
                )

            # ----------------------------------------------------------
            # Store references.
            # ----------------------------------------------------------

            task_reference = (
                item.get("id")
                or item.get("task_id")
                or title
            )

            task_reference_map[
                str(task_reference)
            ] = task_id

            task_reference_map[
                title
            ] = task_id

            task = Task(
                id=task_id,

                title=title,

                description=str(
                    item.get(
                        "description",
                        "",
                    )
                ),

                capability=capability,

                task_type=self._parse_task_type(
                    item.get(
                        "task_type",
                        "EXECUTE",
                    )
                ),

                priority=self._parse_task_priority(
                    item.get(
                        "priority",
                        "MEDIUM",
                    )
                ),

                parameters=(
                    item.get(
                        "parameters",
                        {},
                    )
                    if isinstance(
                        item.get(
                            "parameters",
                            {},
                        ),
                        dict,
                    )
                    else {}
                ),

                dependencies=[],

                assigned_executor=(
                    item.get(
                        "assigned_executor"
                    )
                ),
            )

            tasks.append(
                task
            )

        # --------------------------------------------------------------
        # Second pass
        #
        # Resolve dependency references.
        # --------------------------------------------------------------

        for index, item in enumerate(items):

            dependencies = item.get(
                "dependencies",
                [],
            )

            if dependencies is None:
                dependencies = []

            if not isinstance(
                dependencies,
                list,
            ):

                dependencies = [
                    dependencies
                ]

            resolved_dependencies = []

            for dependency in dependencies:

                dependency_str = str(
                    dependency
                ).strip()

                if not dependency_str:
                    continue

                resolved_dependency = (
                    task_reference_map.get(
                        dependency_str
                    )
                )

                # ------------------------------------------------------
                # If the LLM already returned a real task ID, preserve
                # it.
                # ------------------------------------------------------

                if resolved_dependency is None:
                    resolved_dependency = (
                        dependency_str
                    )

                # ------------------------------------------------------
                # Prevent self dependency.
                # ------------------------------------------------------

                if (
                    resolved_dependency
                    == tasks[index].id
                ):
                    continue

                if (
                    resolved_dependency
                    not in resolved_dependencies
                ):

                    resolved_dependencies.append(
                        resolved_dependency
                    )

            tasks[index].dependencies = (
                resolved_dependencies
            )

        return tasks

    # ==================================================================
    # TASK TYPE PARSER
    # ==================================================================

    @staticmethod
    def _parse_task_type(
        value: Any,
    ) -> TaskType:
        """
        Safely convert an LLM task_type into TaskType.
        """

        if isinstance(
            value,
            TaskType,
        ):
            return value

        normalized = str(
            value or "EXECUTE"
        ).strip().upper()

        try:

            return TaskType[
                normalized
            ]

        except KeyError as exc:

            valid_values = [
                member.name
                for member in TaskType
            ]

            raise ValueError(
                f"Invalid task_type '{normalized}'. "
                f"Expected one of: {valid_values}"
            ) from exc

    # ==================================================================
    # TASK PRIORITY PARSER
    # ==================================================================

    @staticmethod
    def _parse_task_priority(
        value: Any,
    ) -> TaskPriority:
        """
        Safely convert an LLM priority into TaskPriority.
        """

        if isinstance(
            value,
            TaskPriority,
        ):
            return value

        normalized = str(
            value or "MEDIUM"
        ).strip().upper()

        try:

            return TaskPriority[
                normalized
            ]

        except KeyError as exc:

            valid_values = [
                member.name
                for member in TaskPriority
            ]

            raise ValueError(
                f"Invalid priority '{normalized}'. "
                f"Expected one of: {valid_values}"
            ) from exc

    # ==================================================================
    # EXECUTION GRAPH BUILDER
    # ==================================================================

    def _build_execution_plan(
        self,
        request: PlanningRequest,
        tasks: List[Task],
    ) -> ExecutionPlan:
        """
        Build the TaskGraph and schedule it.
        """

        graph = TaskGraph()

        # --------------------------------------------------------------
        # Add tasks
        # --------------------------------------------------------------

        for task in tasks:

            graph.add_task(
                task
            )

        # --------------------------------------------------------------
        # Add dependencies
        # --------------------------------------------------------------

        task_ids = {
            task.id
            for task in tasks
        }

        for task in tasks:

            for dependency in (
                task.dependencies
            ):

                if dependency not in task_ids:

                    logger.warning(
                        "Skipping unresolved dependency | "
                        "task=%s | dependency=%s",
                        task.id,
                        dependency,
                    )

                    continue

                graph.add_dependency(
                    task.id,
                    dependency,
                )

        # --------------------------------------------------------------
        # Schedule graph
        # --------------------------------------------------------------

        scheduler = Scheduler()

        layers = scheduler.schedule(
            graph
        )

        # --------------------------------------------------------------
        # Flatten execution order
        # --------------------------------------------------------------

        execution_order = [
            task.id
            for layer in layers
            for task in layer
        ]

        # --------------------------------------------------------------
        # Root tasks
        # --------------------------------------------------------------

        root_tasks = [
            task.id
            for task in graph.root_tasks()
        ]

        # --------------------------------------------------------------
        # Leaf tasks
        # --------------------------------------------------------------

        leaf_tasks = [
            task.id
            for task in graph.leaf_tasks()
        ]

        # --------------------------------------------------------------
        # Build ExecutionPlan
        # --------------------------------------------------------------

        execution_plan = ExecutionPlan(
            id=str(
                uuid.uuid4()
            ),

            query=request.query,

            intent=request.intent,

            graph=graph,

            execution_order=execution_order,

            root_tasks=root_tasks,

            leaf_tasks=leaf_tasks,
        )

        logger.info(
            "Execution plan created | "
            "plan_id=%s | "
            "tasks=%d | "
            "roots=%d | "
            "leaves=%d",
            execution_plan.id,
            len(tasks),
            len(root_tasks),
            len(leaf_tasks),
        )

        return execution_plan

    # ==================================================================
    # TASK FACTORY
    # ==================================================================

    def _task(
        self,
        title: str,
        description: str,
        capability: str,
        task_type: TaskType = TaskType.EXTRACT_INFORMATION,
        parameters: Optional[
            Dict[str, Any]
        ] = None,
        dependencies: Optional[
            List[str]
        ] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_executor: Optional[str] = None,
    ) -> Task:
        """
        Convenience factory for creating Task objects.
        """

        return Task(
            id=str(
                uuid.uuid4()
            ),

            title=title,

            description=description,

            capability=capability,

            task_type=task_type,

            parameters=parameters or {},

            dependencies=dependencies or [],

            priority=priority,

            assigned_executor=assigned_executor,
        )