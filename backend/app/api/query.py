from fastapi import APIRouter, Depends

from app.db.models.request import QueryRequest
from app.db.models.response import QueryResponse

from app.planning.models.planning_request import PlanningRequest


api_router = APIRouter()


# ----------------------------------------------------------
# Dependency Injection
# ----------------------------------------------------------

def get_container():

    from app.container import container

    return container



def get_planner_service():

    container = get_container()

    return container.planner_service



def get_orchestration_service():

    container = get_container()

    return container.orchestration_service



# ----------------------------------------------------------
# Query Endpoint
# ----------------------------------------------------------

@api_router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    planner_service = Depends(get_planner_service),
    orchestration_service = Depends(get_orchestration_service),
):
    """
    Main API endpoint.

    Pipeline

        Client
            |
            ▼
        Planner
            |
            ▼
        Orchestration Service
            |
            ├── Memory Retrieval
            ├── Adaptive Retrieval
            ├── Agent Execution
            ├── Tool Execution
            ├── Context Builder
            ├── Final Response
            └── Memory Update
            |
            ▼
        API Response
    """


    # ------------------------------------------------------
    # 1. Build planning request
    # ------------------------------------------------------

    planning_request = PlanningRequest(
        original_query=request.query
    )


    # ------------------------------------------------------
    # 2. Generate execution plan
    # ------------------------------------------------------

    execution_plan = planner_service.create_plan(
        planning_request.original_query
    )


    # ------------------------------------------------------
    # 3. Execute orchestration pipeline
    # ------------------------------------------------------

    execution_result = await orchestration_service.execute(
        execution_plan=execution_plan,
        query=request.query,
        conversation_id=getattr(
            request,
            "conversation_id",
            None
        ),
        user_id=getattr(
            request,
            "user_id",
            None
        ),
    )


    # ------------------------------------------------------
    # 4. Format execution steps
    # ------------------------------------------------------

    formatted_steps = [
        task.description
        for task in execution_plan.graph.tasks.values()
    ]


    # ------------------------------------------------------
    # 5. Return response
    # ------------------------------------------------------

    return QueryResponse(
        success=True,
        response=execution_result.response,
        execution_plan=execution_plan,
        steps=formatted_steps,
        tools_used=execution_result.tools_used,
    )