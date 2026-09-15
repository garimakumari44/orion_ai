"""
Task Decomposer

Converts research strategy into
agent tasks.
"""


from .models import (
    ResearchObjective,
    PlannerTask
)


class TaskDecomposer:
    """
    Creates tasks for specialized agents.
    """


    async def create_tasks(
        self,
        objective: ResearchObjective
    ):

        tasks = []


        for index, agent in enumerate(
            objective.analysis_required
        ):

            tasks.append(

                PlannerTask(

                    task_id=f"TASK_{index+1}",

                    agent=agent,

                    description=(
                        f"Perform {agent} "
                        "analysis for "
                        f"{objective.company}"
                    ),

                    priority="medium",

                    dependencies=[]
                )
            )


        return tasks