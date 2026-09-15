"""
Agent State

Lifecycle states for agent execution.
"""

from enum import Enum


class AgentState(str, Enum):

    CREATED = "created"

    INITIALIZING = "initializing"

    RUNNING = "running"

    WAITING = "waiting"

    COMPLETED = "completed"

    FAILED = "failed"


    @property
    def is_terminal(self) -> bool:
        """
        Whether the agent execution has finished.
        """

        return self in {
            AgentState.COMPLETED,
            AgentState.FAILED,
        }


    @property
    def is_active(self) -> bool:
        """
        Whether the agent is currently executing.
        """

        return self in {
            AgentState.INITIALIZING,
            AgentState.RUNNING,
            AgentState.WAITING,
        }