from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.llm.manager import LLMManager

from .models.execution_plan import ExecutionPlan
from .models.task_graph import TaskGraph


logger = logging.getLogger(__name__)


class ExecutionPlanBuilder:
    """
    Builds the final ExecutionPlan from a TaskGraph.

    The builder does not create tasks, assign agents, execute agents,
    execute tools, retrieve memory, or schedule tasks.

    It only validates and enriches the already-created execution graph.
    """

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
    ) -> None:
        self.llm_manager = llm_manager

    # ==========================================================
    # MAIN BUILDER
    # ==========================================================

    def build(
        self,
        graph: TaskGraph,
        execution_order: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        include_explanation: bool = False,
    ) -> ExecutionPlan:

        metadata = dict(metadata or {})

        self._validate_graph(graph)

        self._validate_execution_order(
            graph=graph,
            execution_order=execution_order,
        )

        metadata["memory"] = self._build_memory_config(graph)

        self._populate_execution_details(graph)

        root_tasks = self._find_root_tasks(graph)
        leaf_tasks = self._find_leaf_tasks(graph)

        if include_explanation and self.llm_manager:
            metadata["explanation"] = (
                self._generate_explanation(
                    graph,
                    execution_order,
                )
            )

        return ExecutionPlan(
            graph=graph,
            execution_order=execution_order,
            root_tasks=root_tasks,
            leaf_tasks=leaf_tasks,
            metadata=metadata,
        )

    # ==========================================================
    # GRAPH VALIDATION
    # ==========================================================

    def _validate_graph(
        self,
        graph: TaskGraph,
    ) -> None:

        if graph is None:
            raise ValueError(
                "Cannot create execution plan from None graph"
            )

        if not graph.tasks:
            raise ValueError(
                "Cannot create execution plan from empty graph"
            )

        for task_id, task in graph.tasks.items():

            if task is None:
                raise ValueError(
                    f"Task {task_id} is None"
                )

            task_type = getattr(
                task,
                "task_type",
                None,
            )

            if not task_type:
                raise ValueError(
                    f"Task {task_id} missing task_type"
                )

            agent_name = getattr(
                task,
                "agent_name",
                None,
            )

            if not agent_name:
                raise ValueError(
                    f"Task {task_id} "
                    f"('{getattr(task, 'title', 'unknown')}') "
                    "missing agent_name"
                )

            if not isinstance(agent_name, str):
                raise ValueError(
                    f"Task {task_id} agent_name must be a string"
                )

            if not agent_name.strip():
                raise ValueError(
                    f"Task {task_id} agent_name cannot be empty"
                )

            dependencies = getattr(
                task,
                "dependencies",
                [],
            )

            if dependencies is None:
                continue

            if not isinstance(dependencies, list):
                raise ValueError(
                    f"Task {task_id} dependencies must be a list"
                )

            for dependency_id in dependencies:
                if dependency_id not in graph.tasks:
                    raise ValueError(
                        f"Task {task_id} depends on "
                        f"unknown task {dependency_id}"
                    )

    # ==========================================================
    # EXECUTION ORDER VALIDATION
    # ==========================================================

    def _validate_execution_order(
        self,
        graph: TaskGraph,
        execution_order: List[str],
    ) -> None:

        if execution_order is None:
            raise ValueError(
                "Execution order cannot be None"
            )

        if not isinstance(execution_order, list):
            raise ValueError(
                "Execution order must be a list"
            )

        graph_task_ids = set(graph.tasks.keys())
        execution_task_ids = set(execution_order)

        unknown_tasks = (
            execution_task_ids - graph_task_ids
        )

        if unknown_tasks:
            raise ValueError(
                "Execution order contains "
                f"unknown task IDs: {unknown_tasks}"
            )

        missing_tasks = (
            graph_task_ids - execution_task_ids
        )

        if missing_tasks:
            raise ValueError(
                "Execution order is missing "
                f"task IDs: {missing_tasks}"
            )

        if len(execution_order) != len(execution_task_ids):
            raise ValueError(
                "Execution order contains duplicate task IDs"
            )

    # ==========================================================
    # MEMORY CONFIGURATION
    # ==========================================================

    def _build_memory_config(
        self,
        graph: TaskGraph,
    ) -> Dict[str, Any]:

        task_types = {
            self._task_type_value(task)
            for task in graph.tasks.values()
        }

        research_tasks = {
            "research",
            "search",
            "web_search",
            "dense_retrieval",
            "hybrid_retrieval",
            "graph_retrieval",
            "company_lookup",
            "financial_data",
            "market_data",
            "fundamentals",
            "sec_filing",
            "news_search",
        }

        writing_tasks = {
            "summarize",
            "generate_report",
            "write_report",
        }

        include_research = bool(
            task_types & research_tasks
        )

        include_preferences = bool(
            task_types & writing_tasks
        )

        return {
            "retrieve": True,
            "store": True,
            "top_k": 8,
            "ranking": "hybrid",
            "context_builder": True,
            "stores": {
                "working": True,
                "episodic": include_research,
                "semantic": include_research,
                "procedural": False,
                "research": include_research,
                "preferences": include_preferences,
            },
        }

    # ==========================================================
    # TASK ENRICHMENT
    # ==========================================================

    def _populate_execution_details(
        self,
        graph: TaskGraph,
    ) -> None:

        for task in graph.tasks.values():

            existing_capability = getattr(
                task,
                "capability",
                None,
            )

            if not existing_capability:
                task.capability = self._infer_capability(task)

            task.parameters = self._build_parameters(task)

            if hasattr(task, "dependencies"):
                task.dependencies = list(
                    getattr(
                        task,
                        "dependencies",
                        [],
                    )
                    or []
                )

            task.priority = self._infer_priority(task)
            task.cost = self._estimate_cost(task)

    # ==========================================================
    # TASK TYPE
    # ==========================================================

    @staticmethod
    def _task_type_value(task) -> str:

        task_type = getattr(
            task,
            "task_type",
            "",
        )

        if hasattr(task_type, "value"):
            return str(task_type.value)

        return str(task_type)

    # ==========================================================
    # CAPABILITY
    # ==========================================================

    def _infer_capability(
        self,
        task,
    ) -> str:

        mapping = {
            "search": "search.retrieve",
            "web_search": "search.web",
            "github_search": "github.search",
            "news_search": "news.search",

            "company_lookup": "knowledge.company.lookup",
            "graph_retrieval": "knowledge.graph.query",

            "financial_data": "finance.market.data",
            "market_data": "finance.market.data",
            "fundamentals": "finance.fundamentals",
            "sec_filing": "finance.sec.filing",

            "research": "research.retrieve",

            "summarize": "llm.summarize",
            "analyze": "llm.analyze",
            "compare": "llm.compare",
            "classify": "llm.classify",

            "dense_retrieval": "retrieval.dense",
            "sparse_retrieval": "retrieval.sparse",
            "hybrid_retrieval": "retrieval.hybrid",
            "rerank": "retrieval.rerank",
            "compress_context": "retrieval.compress",

            "memory_store": "memory.store",
            "memory_extract": "memory.extract",
            "memory_consolidate": "memory.consolidate",

            "generate_report": "report.generate",
            "write_report": "report.generate",
        }

        task_type = self._task_type_value(task)

        return mapping.get(
            task_type,
            "general.execute",
        )

    # ==========================================================
    # PARAMETERS
    # ==========================================================

    def _build_parameters(
        self,
        task,
    ) -> Dict[str, Any]:

        existing_parameters = getattr(
            task,
            "parameters",
            None,
        )

        parameters: Dict[str, Any] = {}

        if isinstance(existing_parameters, dict):
            parameters.update(existing_parameters)

        allowed_fields = [
            "query",
            "company",
            "repository",
            "url",
            "topic",
            "language",
            "time_range",
            "filters",
            "limit",
            "top_k",
            "retrieval_mode",
            "collection",
            "namespace",
            "embedding_model",
            "reranker",
            "include_memory",
            "memory_types",
            "include_graph",
            "include_web",
            "score_threshold",
        ]

        for field in allowed_fields:
            value = getattr(
                task,
                field,
                None,
            )

            if value is not None:
                parameters[field] = value

        task_metadata = getattr(
            task,
            "metadata",
            None,
        )

        if isinstance(task_metadata, dict):
            parameters.update(task_metadata)

        return parameters

    # ==========================================================
    # PRIORITY
    # ==========================================================

    def _infer_priority(
        self,
        task,
    ) -> str:

        high_priority = {
            "market_data",
            "financial_data",
            "news_search",
            "alert",
            "generate_report",
            "reason",
            "validate",
        }

        task_type = self._task_type_value(task)

        if task_type in high_priority:
            return "high"

        return "medium"

    # ==========================================================
    # COST
    # ==========================================================

    def _estimate_cost(
        self,
        task,
    ) -> str:

        expensive_tasks = {
            "web_search",
            "dense_retrieval",
            "generate_report",
            "write_report",
            "analyze",
            "reason",
        }

        task_type = self._task_type_value(task)

        if task_type in expensive_tasks:
            return "high"

        return "low"

    # ==========================================================
    # GRAPH HELPERS
    # ==========================================================

    def _find_root_tasks(
        self,
        graph: TaskGraph,
    ) -> List[str]:

        return [
            task_id
            for task_id in graph.tasks
            if not graph.dependencies.get(task_id)
        ]

    def _find_leaf_tasks(
        self,
        graph: TaskGraph,
    ) -> List[str]:

        return [
            task_id
            for task_id in graph.tasks
            if not graph.children.get(task_id)
        ]

    # ==========================================================
    # EXPLANATION
    # ==========================================================

    def _generate_explanation(
        self,
        graph: TaskGraph,
        execution_order: List[str],
    ) -> str:

        if self.llm_manager is None:
            return (
                "Execution plan generated successfully."
            )

        tasks = []

        for task_id in execution_order:

            task = graph.tasks.get(task_id)

            if task is None:
                continue

            tasks.append(
                {
                    "name": getattr(
                        task,
                        "name",
                        getattr(
                            task,
                            "title",
                            "unknown",
                        ),
                    ),
                    "description": getattr(
                        task,
                        "description",
                        "",
                    ),
                    "task_type": self._task_type_value(task),
                    "capability": getattr(
                        task,
                        "capability",
                        None,
                    ),
                    "agent_name": getattr(
                        task,
                        "agent_name",
                        None,
                    ),
                    "dependencies": getattr(
                        task,
                        "dependencies",
                        [],
                    ),
                }
            )

        prompt = f"""
Explain this AI execution plan.

Tasks:
{tasks}

Execution order:
{execution_order}

Rules:
- Explain the reasoning flow.
- Explain task dependencies.
- Explain assigned agents.
- Explain capabilities where useful.
- Keep the explanation concise.
- Do not mention internal Python code.
""".strip()

        try:
            result = self.llm_manager.generate(
                prompt=prompt,
                task="planning_explanation",
                temperature=0.2,
                max_tokens=500,
            )

            if result is None:
                return (
                    "Execution plan generated successfully."
                )

            return str(result).strip()

        except Exception as exc:
            logger.warning(
                "Failed to generate execution-plan explanation: %s",
                exc,
            )

            return (
                "Execution plan generated successfully. "
                "Detailed explanation was unavailable."
            )
