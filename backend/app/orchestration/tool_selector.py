"""
app/orchestration/tool_selector.py

Responsible only for selecting the best candidate.

It does not:
- execute tools
- perform policy validation
- own health state
"""

from __future__ import annotations

from typing import Sequence

from app.orchestration.capability import Capability
from app.orchestration.tool_registry import ToolRegistry
from app.tools.base.base_tool import BaseTool


class ToolSelectionError(Exception):
    """
    Raised when no suitable tool can be selected.
    """


class ToolSelector:

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:

        self.registry = registry

    # =========================================================
    # Capability Selection
    # =========================================================

    def select(
        self,
        capability: Capability,
    ) -> BaseTool:

        candidates = (
            self.registry.find_by_capability(
                capability
            )
        )

        if not candidates:

            raise ToolSelectionError(
                f"No tool registered for capability "
                f"'{capability.value}'."
            )

        return self.select_from_candidates(
            candidates
        )

    # =========================================================
    # Candidate Selection
    # =========================================================

    def select_from_candidates(
        self,
        candidates: Sequence[BaseTool],
    ) -> BaseTool:

        candidates = list(candidates)

        if not candidates:

            raise ToolSelectionError(
                "No candidates available."
            )

        # Only select enabled tools here.
        # Health and policy are handled upstream.
        enabled = [
            tool
            for tool in candidates
            if getattr(
                tool,
                "enabled",
                True,
            )
        ]

        if not enabled:

            raise ToolSelectionError(
                "No enabled tools available."
            )

        return max(
            enabled,
            key=lambda tool: getattr(
                tool,
                "priority",
                0,
            ),
        )