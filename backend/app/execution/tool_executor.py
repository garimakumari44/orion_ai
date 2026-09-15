from __future__ import annotations

import logging
from typing import Any

from app.execution.models.task_result import TaskResult
from app.planning.models.task_node import TaskNode
from app.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes a selected tool for a task.

    Responsibilities
    ----------------
    - Execute the selected tool
    - Catch execution errors
    - Log execution
    - Return a TaskResult

    Future enhancements
    -------------------
    - Retries
    - Timeouts
    - Metrics
    - Tracing
    - Circuit breakers
    """

    async def execute(
        self,
        tool: BaseTool,
        task: TaskNode,
    ) -> TaskResult:
        """
        Execute a tool for the given task.

        Parameters
        ----------
        tool : BaseTool
            Tool selected by the OrchestrationService.

        task : TaskNode
            Task to execute.

        Returns
        -------
        TaskResult
        """

        logger.info(
            "Executing tool '%s' for task '%s'",
            tool.name,
            task.id,
        )

        try:
            output: Any = await tool.run(task)

            logger.info(
                "Tool '%s' completed successfully.",
                tool.name,
            )

            return TaskResult(
                task_id=task.id,
                success=True,
                output=output,
            )

        except Exception as exc:
            logger.exception(
                "Tool '%s' failed for task '%s'",
                tool.name,
                task.id,
            )

            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(exc),
            )