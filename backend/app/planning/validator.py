"""
Validates the planning graph before scheduling.

Responsible only for structural DAG validation.
"""

from typing import Set

from .models.task_graph import TaskGraph


class ValidationError(Exception):
    """
    Raised when TaskGraph validation fails.
    """


class GraphValidator:
    """
    Validates TaskGraph objects before execution.

    Responsibilities
    ----------------
    ✓ Empty graph detection
    ✓ Duplicate task ids
    ✓ Missing dependencies
    ✓ Self dependencies
    ✓ Cycles
    ✓ Unknown task types

    Does NOT:
    - Execute tasks
    - Validate tools
    - Validate domain logic
    - Validate retrieval quality
    """


    ALLOWED_TASK_TYPES = {

        # Planning
        "planning",
        "research",
        "analysis",
        "comparison",
        "summarization",
        "coding",

        # Retrieval
        "query_rewrite",
        "dense_retrieval",
        "sparse_retrieval",
        "graph_retrieval",
        "memory_retrieval",
        "retrieval_merge",
        "reranking",
        "compression",
        "context_builder",
    }


    def validate(
        self,
        graph: TaskGraph
    ) -> None:
        """
        Validate complete graph.
        """

        self.validate_not_empty(graph)

        self.validate_duplicate_ids(graph)

        self.validate_dependencies_exist(graph)

        self.validate_self_dependencies(graph)

        self.validate_task_types(graph)

        self.validate_no_cycles(graph)



    def validate_not_empty(
        self,
        graph: TaskGraph
    ) -> None:

        if not graph.tasks:
            raise ValidationError(
                "Task graph cannot be empty."
            )



    def validate_duplicate_ids(
        self,
        graph: TaskGraph
    ) -> None:

        ids: Set[str] = set()

        for task in graph.tasks.values():

            if task.id in ids:
                raise ValidationError(
                    f"Duplicate task id '{task.id}'."
                )

            ids.add(task.id)



    def validate_dependencies_exist(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            for dependency in task.dependencies:

                if dependency not in graph.tasks:

                    raise ValidationError(
                        f"Task '{task.id}' depends on "
                        f"missing task '{dependency}'."
                    )



    def validate_self_dependencies(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            if task.id in task.dependencies:

                raise ValidationError(
                    f"Task '{task.id}' depends on itself."
                )



    def validate_task_types(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            task_type = getattr(
                task,
                "task_type",
                None
            )


            if not task_type:

                raise ValidationError(
                    f"Task '{task.id}' has no task type."
                )


            if task_type.lower() not in self.ALLOWED_TASK_TYPES:

                raise ValidationError(
                    f"Unknown task type '{task_type}'."
                )



    def validate_no_cycles(
        self,
        graph: TaskGraph
    ) -> None:

        visited: Set[str] = set()

        visiting: Set[str] = set()


        for task_id in graph.tasks:

            if task_id not in visited:

                self._dfs(
                    task_id,
                    graph,
                    visited,
                    visiting,
                )



    def _dfs(
        self,
        task_id: str,
        graph: TaskGraph,
        visited: Set[str],
        visiting: Set[str],
    ) -> None:

        visiting.add(task_id)


        task = graph.tasks[task_id]


        for dependency in task.dependencies:


            if dependency in visiting:

                raise ValidationError(
                    f"Cycle detected involving '{dependency}'."
                )


            if dependency not in visited:

                self._dfs(
                    dependency,
                    graph,
                    visited,
                    visiting,
                )


        visiting.remove(task_id)

        visited.add(task_id)