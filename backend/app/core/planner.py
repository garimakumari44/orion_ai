# core/planner.py

from typing import Dict, List


class Planner:
    """
    Converts an intent into an execution plan.
    """

    def create_plan(self, intent: Dict) -> List[Dict]:
        tasks: List[Dict] = []

        # Search task
        if intent.get("requires_search", False):
            tasks.append({
                "task": "search_web",
                "description": "Search the web for information"
            })

        # Summarization task
        if intent.get("requires_summary", False):
            tasks.append({
                "task": "summarize",
                "description": "Summarize the collected information"
            })

        # Default task
        if not tasks:
            tasks.append({
                "task": "respond",
                "description": "Answer directly without external tools"
            })

        return tasks