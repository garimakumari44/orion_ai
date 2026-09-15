from backend.app.services.planner_service import PlannerService

planner = PlannerService()

plan = planner.create_plan(
    "Compare OpenAI and Anthropic"
)

print(plan)