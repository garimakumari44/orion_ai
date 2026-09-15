"""
app/orchestration/service.py

Central orchestration service.

Flow:

Capability
    |
    v
Tool Registry
    |
    v
Health Monitor
    |
    v
Policy Engine
    |
    v
Tool Selector
    |
    v
Selected Tool
"""

from __future__ import annotations

from app.orchestration.capability import Capability
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.policies import PolicyEngine
from app.orchestration.tool_registry import ToolRegistry
from app.orchestration.tool_selector import (
    ToolSelector,
    ToolSelectionError,
)
from app.tools.base.base_tool import BaseTool


class OrchestrationService:

    def __init__(
        self,
        registry: ToolRegistry,
        selector: ToolSelector,
        health_monitor: HealthMonitor,
        policy_engine: PolicyEngine,
    ) -> None:

        self.registry = registry
        self.selector = selector
        self.health_monitor = health_monitor
        self.policy_engine = policy_engine

    # =========================================================
    # Tool Selection
    # =========================================================

    def select_tool(
        self,
        capability: Capability,
    ) -> BaseTool:
        """
        Select best tool for capability.
        """

        # -----------------------------------------------------
        # 1. Discover candidates
        # -----------------------------------------------------

        candidates = (
            self.registry.find_by_capability(
                capability
            )
        )

        if not candidates:

            raise ValueError(
                f"No tool supports capability "
                f"'{capability.value}'."
            )

        # -----------------------------------------------------
        # 2. Register health state
        # -----------------------------------------------------

        for tool in candidates:

            self.health_monitor.register_tool(
                tool.name
            )

        # -----------------------------------------------------
        # 3. Filter runtime-unhealthy tools
        # -----------------------------------------------------

        healthy_tools = [
            tool
            for tool in candidates
            if self.health_monitor.is_healthy(
                tool.name
            )
        ]

        if not healthy_tools:

            raise RuntimeError(
                f"No healthy tools available for "
                f"capability '{capability.value}'."
            )

        # -----------------------------------------------------
        # 4. Apply policy
        # -----------------------------------------------------

        allowed_tools = (
            self.policy_engine.filter(
                healthy_tools,
                capability=capability,
            )
        )

        if not allowed_tools:

            raise PermissionError(
                f"All tools for capability "
                f"'{capability.value}' were rejected "
                "by policy."
            )

        # -----------------------------------------------------
        # 5. Select
        # -----------------------------------------------------

        try:

            return (
                self.selector.select_from_candidates(
                    allowed_tools
                )
            )

        except ToolSelectionError:
            raise RuntimeError(
                f"Unable to select tool for "
                f"capability '{capability.value}'."
            )