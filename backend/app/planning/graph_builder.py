
"""
app/planning/graph_builder.py

Graph Builder

Converts planned Tasks into the canonical TaskGraph.

Responsibilities:
- Register tasks
- Connect dependencies
- Prepare graph structure

Does NOT:
- Execute tasks
- Schedule tasks
- Validate cycles
- Run tools

Canonical dependency contract:

    task_id depends on dependency_id

Example:

    Company Research
           |
           v
    Financial Analysis

Therefore:

    financial_analysis.dependencies = [
        "company_research"
    ]
"""

from __future__ import annotations

import logging
from typing import List

from app.planning.models.task import Task
from app.planning.models.task_graph import TaskGraph

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Converts planned tasks into a TaskGraph.
    """

    # ======================================================
    # Build
    # ======================================================

    def build(
        self,
        tasks: List[Task],
    ) -> TaskGraph:
        """
        Build a dependency graph from planned Tasks.

        Flow:

            Planned Tasks
                  |
                  v
            GraphBuilder
                  |
                  v
              TaskGraph
        """

        if not tasks:
            raise ValueError(
                "Cannot build graph from empty task list."
            )

        graph = TaskGraph()

        # ==================================================
        # Register tasks
        # ==================================================

        for task in tasks:

            if not isinstance(task, Task):
                raise TypeError(
                    "GraphBuilder requires Task instances. "
                    f"Got {type(task).__name__}."
                )

            if not task.id:
                raise ValueError(
                    "Task is missing an id."
                )

            if task.id in graph.tasks:
                raise ValueError(
                    f"Duplicate task id detected: {task.id}"
                )

            graph.add_task(task)

        # ==================================================
        # Connect dependencies
        # ==================================================

        for task in tasks:

            dependencies = (
                getattr(
                    task,
                    "dependencies",
                    [],
                )
                or []
            )

            for dependency_id in dependencies:

                dependency_id = str(
                    dependency_id
                )

                # ------------------------------------------
                # Every dependency must reference a
                # registered task.
                # ------------------------------------------

                if dependency_id not in graph.tasks:

                    raise ValueError(
                        f"Task '{task.id}' depends on "
                        f"unknown task '{dependency_id}'."
                    )

                # ------------------------------------------
                # Canonical contract:
                #
                # task_id depends on dependency_id
                #
                # Example:
                #
                # financial_analysis
                #     depends on
                # company_research
                #
                # therefore:
                #
                # task_id="financial_analysis"
                # dependency_id="company_research"
                # ------------------------------------------

                graph.add_dependency(
                    task_id=task.id,
                    dependency_id=dependency_id,
                )

        # ==================================================
        # Attach graph metadata
        # ==================================================

        graph.metadata = {
            "total_tasks": len(
                graph.tasks
            ),
            "total_dependencies": (
                self._count_dependencies(
                    graph
                )
            ),
            "root_candidates": (
                self._count_roots(
                    graph
                )
            ),
        }

        logger.info(
            "TaskGraph built | "
            "tasks=%d | "
            "dependencies=%d | "
            "roots=%d",
            graph.metadata["total_tasks"],
            graph.metadata["total_dependencies"],
            graph.metadata["root_candidates"],
        )

        return graph

    # ======================================================
    # Graph statistics
    # ======================================================

    @staticmethod
    def _count_dependencies(
        graph: TaskGraph,
    ) -> int:
        """
        Count all dependency edges in the graph.
        """

        count = 0

        for dependencies in (
            graph.dependencies.values()
        ):
            count += len(
                dependencies
            )

        return count

    @staticmethod
    def _count_roots(
        graph: TaskGraph,
    ) -> int:
        """
        Count tasks that have no dependencies.

        Root tasks are eligible to execute first.
        """

        roots = 0

        for task_id in graph.tasks:

            if not graph.dependencies.get(
                task_id
            ):
                roots += 1

        return roots

