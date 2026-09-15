import pytest

from app.planning.planner import Planner
from app.planning.models.planning_request import PlanningRequest
from app.execution.execution_engine import ExecutionEngine


@pytest.mark.asyncio
async def test_execution_pipeline():
    """
    Integration test:
    Planner -> ExecutionEngine
    """

    planner = Planner()
    engine = ExecutionEngine()

    request = PlanningRequest(
        query="Find AI startups in India and summarize them.",
        intent="research",
    )

    plan = planner.create_plan(request)

    assert plan is not None
    assert plan.total_tasks > 0
    assert plan.total_execution_steps > 0

    print("\n===== PLANNER OUTPUT =====")

    for task in plan.graph:
        print(task)

    # Execute asynchronously
    result = await engine.execute(plan)

    print("\n===== EXECUTION OUTPUT =====")
    print(result)

    assert result is not None
    assert result.success is True