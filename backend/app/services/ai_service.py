"""
Central AI Service.

This service is the main entry point for every AI request.
It coordinates agent selection, execution, and response synthesis.

API Layer
    ↓
AIService
    ↓
AgentSelector
    ↓
CollaborationManager
    ↓
Agents
"""

from __future__ import annotations

from typing import Any

from app.agents.manager.agent_selector import AgentSelector
from app.collaboration.collaboration_manager import CollaborationManager


class AIService:
    """
    Coordinates the complete AI workflow.

    Responsibilities
    ----------------
    - Determine which agents should handle a query.
    - Execute the selected agents.
    - Combine their outputs.
    - Return a unified response.
    """

    def __init__(self) -> None:
        self.selector = AgentSelector()
        self.collaboration = CollaborationManager()

    async def process(self, query: str) -> dict[str, Any]:
        """
        Process a user query.

        Parameters
        ----------
        query:
            User request.

        Returns
        -------
        dict
            Unified response.
        """

        # Step 1
        selected_agents = await self.selector.select_agents(query)

        if not selected_agents:
            return {
                "success": False,
                "response": "No suitable agent found.",
                "agents": [],
            }

        # Step 2
        result = await self.collaboration.execute(
            query=query,
            agents=selected_agents,
        )

        return {
            "success": True,
            "query": query,
            "agents": [agent.name for agent in selected_agents],
            "response": result,
        }