from __future__ import annotations

import logging

from app.execution.execution_engine import ExecutionEngine
from app.execution.models.execution_result import ExecutionResult
from app.planning.models.execution_plan import ExecutionPlan

logger = logging.getLogger(__name__)


class Executor:
    """
    High-level coordinator responsible for executing an ExecutionPlan.

    Responsibilities
    ----------------
    - Accept an ExecutionPlan
    - Perform lightweight validation
    - Delegate execution to the ExecutionEngine
    - Return the aggregated ExecutionResult

    The Executor intentionally contains no business logic,
    scheduling logic, agent logic, or LLM logic.
    """

    def __init__(self, engine: ExecutionEngine):
        self.engine = engine

    async def execute(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionResult:
        """
        Execute the supplied execution plan.

        Parameters
        ----------
        plan:
            Execution plan produced by the planner.

        Returns
        -------
        ExecutionResult
            Aggregated execution result.
        """

        if plan is None:
            raise ValueError("ExecutionPlan cannot be None.")

        logger.info("Starting execution.")

        try:
            result = await self.engine.execute(plan)

            logger.info(
                "Execution completed successfully."
            )

            return result

        except Exception:
            logger.exception("Execution failed.")
            raise