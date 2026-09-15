"""
Planner Router

Routes execution requests to the appropriate subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .strategy_selector import ExecutionStrategy


class RouteTarget(str, Enum):
    LLM = "llm"

    KNOWLEDGE_SYSTEM = "knowledge_system"

    ADAPTIVE_RETRIEVAL = "adaptive_retrieval"

    WEB_SEARCH = "web_search"

    CODE_ENGINE = "code_engine"

    RESEARCH_AGENT = "research_agent"

    MULTI_AGENT_SYSTEM = "multi_agent_system"

    TOOL_EXECUTOR = "tool_executor"


@dataclass
class RouteDecision:
    target: RouteTarget
    use_cache: bool
    stream: bool
    parallel: bool
    reason: str


class PlannerRouter:

    def route(
        self,
        strategy: ExecutionStrategy,
    ) -> RouteDecision:

        if strategy == ExecutionStrategy.DIRECT:
            return RouteDecision(
                target=RouteTarget.LLM,
                use_cache=True,
                stream=True,
                parallel=False,
                reason="Direct language model response.",
            )

        if strategy == ExecutionStrategy.RAG:
            return RouteDecision(
                target=RouteTarget.ADAPTIVE_RETRIEVAL,
                use_cache=True,
                stream=True,
                parallel=False,
                reason="Retrieve knowledge before generation.",
            )

        if strategy == ExecutionStrategy.HYBRID_RAG:
            return RouteDecision(
                target=RouteTarget.KNOWLEDGE_SYSTEM,
                use_cache=True,
                stream=True,
                parallel=True,
                reason="Combine multiple retrieval sources.",
            )

        if strategy == ExecutionStrategy.WEB_SEARCH:
            return RouteDecision(
                target=RouteTarget.WEB_SEARCH,
                use_cache=False,
                stream=True,
                parallel=True,
                reason="Requires external search.",
            )

        if strategy == ExecutionStrategy.CODE:
            return RouteDecision(
                target=RouteTarget.CODE_ENGINE,
                use_cache=False,
                stream=True,
                parallel=False,
                reason="Execute code-related workflow.",
            )

        if strategy == ExecutionStrategy.RESEARCH:
            return RouteDecision(
                target=RouteTarget.RESEARCH_AGENT,
                use_cache=False,
                stream=True,
                parallel=True,
                reason="Research pipeline required.",
            )

        if strategy == ExecutionStrategy.MULTI_AGENT:
            return RouteDecision(
                target=RouteTarget.MULTI_AGENT_SYSTEM,
                use_cache=False,
                stream=True,
                parallel=True,
                reason="Complex multi-agent execution.",
            )

        return RouteDecision(
            target=RouteTarget.LLM,
            use_cache=True,
            stream=True,
            parallel=False,
            reason="Fallback route.",
        )