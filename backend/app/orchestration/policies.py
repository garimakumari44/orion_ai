"""
app/orchestration/policies.py

Policy Engine.

The ToolSelector decides:
    WHICH tool?

The PolicyEngine decides:
    WHETHER the tool is allowed?
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.orchestration.capability import Capability
from app.tools.base.base_tool import BaseTool


@dataclass(slots=True)
class PolicyResult:
    allowed: bool
    reason: Optional[str] = None


class PolicyEngine:

    def __init__(
        self,
    ) -> None:
        pass

    # =========================================================
    # Filter
    # =========================================================

    def filter(
        self,
        tools: list[BaseTool],
        capability: Capability,
    ) -> list[BaseTool]:

        return [
            tool
            for tool in tools
            if self.validate(
                tool,
                capability,
            ).allowed
        ]

    # =========================================================
    # Validation Pipeline
    # =========================================================

    def validate(
        self,
        tool: BaseTool,
        capability: Capability,
    ) -> PolicyResult:

        result = self._check_enabled(
            tool
        )

        if not result.allowed:
            return result

        result = self._check_capability(
            tool,
            capability,
        )

        if not result.allowed:
            return result

        result = self._check_auth(
            tool
        )

        if not result.allowed:
            return result

        result = self._check_health(
            tool
        )

        if not result.allowed:
            return result

        result = self._check_rate_limit(
            tool
        )

        if not result.allowed:
            return result

        return PolicyResult(
            allowed=True
        )

    # =========================================================
    # Enabled
    # =========================================================

    def _check_enabled(
        self,
        tool: BaseTool,
    ) -> PolicyResult:

        if not getattr(
            tool,
            "enabled",
            True,
        ):

            return PolicyResult(
                False,
                f"{tool.name} is disabled.",
            )

        return PolicyResult(True)

    # =========================================================
    # Capability
    # =========================================================

    def _check_capability(
        self,
        tool: BaseTool,
        capability: Capability,
    ) -> PolicyResult:

        capabilities = getattr(
            tool,
            "capabilities",
            [],
        )

        if capability not in capabilities:

            return PolicyResult(
                False,
                (
                    f"{tool.name} does not support "
                    f"{capability.value}."
                ),
            )

        return PolicyResult(True)

    # =========================================================
    # Authentication
    # =========================================================

    def _check_auth(
        self,
        tool: BaseTool,
    ) -> PolicyResult:

        requires_auth = getattr(
            tool,
            "requires_auth",
            False,
        )

        if not requires_auth:
            return PolicyResult(True)

        is_authenticated = getattr(
            tool,
            "is_authenticated",
            None,
        )

        if (
            is_authenticated is not None
            and not is_authenticated()
        ):

            return PolicyResult(
                False,
                f"{tool.name} is not authenticated.",
            )

        return PolicyResult(True)

    # =========================================================
    # Health
    # =========================================================

    def _check_health(
        self,
        tool: BaseTool,
    ) -> PolicyResult:

        is_healthy = getattr(
            tool,
            "is_healthy",
            None,
        )

        if is_healthy is not None:

            if not is_healthy():

                return PolicyResult(
                    False,
                    f"{tool.name} is unhealthy.",
                )

        return PolicyResult(True)

    # =========================================================
    # Rate Limit
    # =========================================================

    def _check_rate_limit(
        self,
        tool: BaseTool,
    ) -> PolicyResult:

        is_rate_limited = getattr(
            tool,
            "is_rate_limited",
            None,
        )

        if (
            is_rate_limited is not None
            and is_rate_limited()
        ):

            return PolicyResult(
                False,
                (
                    f"{tool.name} is currently "
                    "rate limited."
                ),
            )

        return PolicyResult(True)