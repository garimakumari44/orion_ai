# core/router.py

from typing import Dict, List


class Router:
    """
    Routes planner tasks to the appropriate tool.

    Phase 1:
    Executes placeholder implementations.
    """

    def route(self, steps: List[Dict], query: str) -> List[str]:
        """
        Execute every planned task.
        """

        results = []

        for step in steps:
            results.append(self.execute(step, query))

        return results

    def execute(self, task: Dict, query: str) -> str:
        """
        Execute one planner task.
        """

        task_name = task.get("task", "")

        if task_name == "search_web":
            return f"[Placeholder] Searching the web for: {query}"

        elif task_name == "summarize":
            return "[Placeholder] Summarizing search results."

        elif task_name == "respond":
            return f"[Placeholder] Answering directly: {query}"

        return f"[Placeholder] Unknown task: {task_name}"