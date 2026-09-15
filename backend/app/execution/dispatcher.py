
"""
app/execution/dispatcher.py

Responsible for routing execution-ready Tasks to workers.

Responsibilities:
- Dispatch individual tasks
- Dispatch batches of tasks
- Handle routing errors
- Log execution flow

Dispatcher does NOT know:
- agents
- tools
- LLMs
- execution strategy

Execution boundary:

    TaskScheduler
         |
         v
      TaskNode
         |
         v
    ExecutionEngine
         |
         | unwraps node.task
         v
        Task
         |
         v
     Dispatcher
         |
         v
       Worker
         |
         v
    AgentManager
         |
         v
       Agent
"""

from __future__ import annotations

import logging
import time

from app.agents.base.agent_context import AgentContext
from app.execution.models.task_result import TaskResult
from app.execution.worker import Worker
from app.planning.models.task import Task


logger = logging.getLogger(__name__)


class Dispatcher:
    """
    Dispatches execution-ready Tasks to workers.

    The Dispatcher receives only canonical Task objects.

    TaskNode objects belong to the graph/scheduling layer
    and must be unwrapped by the ExecutionEngine before
    reaching this class.
    """

    def __init__(
        self,
        worker: Worker,
    ) -> None:

        self.worker = worker

    async def dispatch(
        self,
        task: Task,
        context: AgentContext | None = None,
    ) -> TaskResult:
        """
        Dispatch a single Task to a Worker.

        Parameters
        ----------
        task:
            Canonical executable Task.

        context:
            Shared runtime AgentContext.
        """

        if not isinstance(task, Task):
            raise TypeError(
                "Dispatcher requires a Task instance, "
                f"got {type(task).__name__}"
            )

        logger.info(
            "Dispatching task '%s'",
            task.id,
        )

        start = time.perf_counter()

        try:

            result = await self.worker.run(
                task=task,
                context=context,
            )

            elapsed = (
                time.perf_counter()
                - start
            )

            logger.info(
                "Task '%s' completed in %.3fs",
                task.id,
                elapsed,
            )

            return result

        except Exception:

            logger.exception(
                "Dispatcher failed while "
                "executing task '%s'",
                task.id,
            )

            raise

    async def dispatch_batch(
        self,
        tasks: list[Task],
        context: AgentContext | None = None,
    ) -> list[TaskResult]:
        """
        Dispatch multiple Tasks.

        Parallel execution is managed by the
        ExecutionEngine, not the Dispatcher.
        """

        logger.info(
            "Dispatching batch (%d tasks)",
            len(tasks),
        )

        results: list[TaskResult] = []

        for task in tasks:

            results.append(
                await self.dispatch(
                    task=task,
                    context=context,
                )
            )

        logger.info(
            "Batch dispatch complete (%d tasks)",
            len(results),
        )

        return results

