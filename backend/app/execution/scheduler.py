
from __future__ import annotations

from collections import deque
from typing import Dict, List

from app.planning.models.task_graph import TaskGraph
from app.planning.models.task_node import TaskNode


class TaskScheduler:
    """
    Produces an execution schedule from a validated TaskGraph.

    Responsibilities
    ----------------
    - Determine execution order
    - Group tasks that can run in parallel
    - Respect dependency constraints

    Does NOT
    --------
    - Execute tasks
    - Modify the graph
    - Validate the graph
    """

    def build_schedule(
        self,
        graph: TaskGraph,
    ) -> List[List[TaskNode]]:
        """
        Build execution stages.

        Returns
        -------
        List[List[TaskNode]]

        Example
        -------
        [
            [node_a],
            [node_b, node_c],
            [node_d],
        ]
        """

        # -------------------------------------------------
        # Remaining dependencies for each task
        # -------------------------------------------------

        in_degree: Dict[str, int] = {
            task.id: len(
                graph.get_dependencies(task.id)
            )
            for task in graph
        }

        # -------------------------------------------------
        # Queue of tasks ready to execute
        # -------------------------------------------------

        ready = deque(
            task
            for task in graph
            if in_degree[task.id] == 0
        )

        stages: List[List[TaskNode]] = []

        # -------------------------------------------------
        # Topological scheduling
        # -------------------------------------------------

        while ready:

            current_stage: List[TaskNode] = []

            # Process all tasks currently ready.
            # These form one parallel execution stage.
            for _ in range(len(ready)):

                task = ready.popleft()

                # -----------------------------------------
                # Convert Task → TaskNode at the execution
                # boundary.
                # -----------------------------------------

                node = TaskNode(
                    task=task,
                    dependencies=set(
                        graph.get_dependencies(task.id)
                    ),
                )

                current_stage.append(node)

                # -----------------------------------------
                # Update dependent tasks
                # -----------------------------------------

                for child_id in graph.get_children(
                    task.id
                ):

                    in_degree[child_id] -= 1

                    if in_degree[child_id] == 0:

                        ready.append(
                            graph.get_task(child_id)
                        )

            stages.append(current_stage)

        return stages

