from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .capability import Capability


@dataclass
class ToolContext:
    """
    Shared execution context passed to every tool.

    A single ToolContext exists for one task execution.
    """

    # ------------------------------------------------------------------
    # Request Information
    # ------------------------------------------------------------------

    query: str
    capability: Capability

    # ------------------------------------------------------------------
    # Execution Identifiers
    # ------------------------------------------------------------------

    task_id: str = field(default_factory=lambda: str(uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid4()))

    # ------------------------------------------------------------------
    # Runtime Configuration
    # ------------------------------------------------------------------

    timeout: float = 30.0
    max_retries: int = 2
    retry_count: int = 0

    # ------------------------------------------------------------------
    # Budget
    # ------------------------------------------------------------------

    cost_budget: float = 1.0

    # ------------------------------------------------------------------
    # Execution History
    # ------------------------------------------------------------------

    attempted_tools: List[str] = field(default_factory=list)

    previous_outputs: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # User Metadata
    # ------------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def add_attempt(self, tool_name: str) -> None:
        """Record that a tool has been attempted."""
        self.attempted_tools.append(tool_name)

    def add_output(self, tool_name: str, output: Any) -> None:
        """Store the output of a tool."""
        self.previous_outputs[tool_name] = output

    def increment_retry(self) -> None:
        """Increase retry count."""
        self.retry_count += 1

    def can_retry(self) -> bool:
        """Check if another retry is allowed."""
        return self.retry_count < self.max_retries

    def remaining_budget(self) -> float:
        """Return remaining cost budget."""
        spent = self.metadata.get("cost_spent", 0.0)
        return max(0.0, self.cost_budget - spent)

    def add_cost(self, amount: float) -> None:
        """Track execution cost."""
        spent = self.metadata.get("cost_spent", 0.0)
        self.metadata["cost_spent"] = spent + amount

    def reset_retries(self) -> None:
        """Reset retry counter."""
        self.retry_count = 0