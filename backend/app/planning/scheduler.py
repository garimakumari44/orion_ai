from typing import List, Set

from .models.task_graph import TaskGraph
from .models.task import Task


class Scheduler:
    """
    Determines execution order of tasks based on dependencies.

    The TaskGraph is the canonical source of dependency
    relationships.
    """

    def __init__(self):
        pass

    def get_initial_tasks(
        self,
        graph: TaskGraph,
    ) -> List[Task]:
        """
        Return tasks with no dependencies.
        """

        return [
            task
            for task in graph.all_tasks()
            if not graph.get_dependencies(task.id)
        ]

    def get_ready_tasks(
        self,
        graph: TaskGraph,
        completed: Set[str],
    ) -> List[Task]:
        """
        Return tasks whose dependencies are satisfied.
        """

        ready = []

        for task in graph.all_tasks():

            if task.id in completed:
                continue

            dependencies = graph.get_dependencies(
                task.id
            )

            if all(
                dependency in completed
                for dependency in dependencies
            ):
                ready.append(task)

        return ready

    def schedule(
        self,
        graph: TaskGraph,
    ) -> List[List[Task]]:
        """
        Produce layered execution order.

        Tasks in the same layer can execute in parallel.

        Raises
        ------
        ValueError
            If the graph contains a dependency cycle.
        """

        completed: Set[str] = set()
        execution_order: List[List[Task]] = []

        total_tasks = len(graph)

        while len(completed) < total_tasks:

            ready = self.get_ready_tasks(
                graph,
                completed,
            )

            if not ready:

                remaining = [
                    task.id
                    for task in graph.all_tasks()
                    if task.id not in completed
                ]

                raise ValueError(
                    "Unable to schedule execution graph. "
                    "Dependency cycle or unresolved dependency "
                    f"detected. Remaining tasks: {remaining}"
                )

            execution_order.append(
                ready
            )

            for task in ready:
                completed.add(
                    task.id
                )

        return execution_order