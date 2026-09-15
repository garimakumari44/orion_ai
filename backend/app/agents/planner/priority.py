"""
Priority Manager

Assigns importance to research tasks.
"""


from .models import PlannerTask


class PriorityManager:
    """
    Determines execution priority.
    """


    HIGH_PRIORITY = [
        "financial",
        "risk",
        "valuation"
    ]


    MEDIUM_PRIORITY = [
        "company",
        "industry",
        "macro"
    ]


    LOW_PRIORITY = [
        "news"
    ]


    def assign_priority(
        self,
        tasks: list[PlannerTask]
    ):

        for task in tasks:


            if task.agent in self.HIGH_PRIORITY:

                task.priority = "high"


            elif task.agent in self.MEDIUM_PRIORITY:

                task.priority = "medium"


            elif task.agent in self.LOW_PRIORITY:

                task.priority = "low"


        return tasks