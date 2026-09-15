"""
Strategy Selector

Determines the overall execution strategy for a query.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .complexity_estimator import ComplexityEstimate
from .retrieval_planner import RetrievalPlan


class ExecutionStrategy(str, Enum):
    DIRECT = "direct"
    RAG = "rag"
    HYBRID_RAG = "hybrid_rag"
    WEB_SEARCH = "web_search"
    AGENT = "agent"
    MULTI_AGENT = "multi_agent"
    CODE = "code"
    RESEARCH = "research"


@dataclass
class StrategyDecision:
    strategy: ExecutionStrategy
    confidence: float
    explanation: str
    estimated_latency: float
    estimated_cost: float


class StrategySelector:

    def select(
        self,
        intent: str,
        complexity: ComplexityEstimate,
        retrieval_plan: RetrievalPlan,
    ) -> StrategyDecision:

        # Greetings / small talk
        if intent in {"greeting", "farewell", "thanks"}:
            return StrategyDecision(
                strategy=ExecutionStrategy.DIRECT,
                confidence=1.0,
                explanation="No retrieval required.",
                estimated_latency=0.2,
                estimated_cost=0.0,
            )

        # External information
        if retrieval_plan.mode.value == "web":
            return StrategyDecision(
                strategy=ExecutionStrategy.WEB_SEARCH,
                confidence=0.95,
                explanation="Requires current external knowledge.",
                estimated_latency=4.0,
                estimated_cost=0.02,
            )

        # Programming
        if complexity.requires_code:
            return StrategyDecision(
                strategy=ExecutionStrategy.CODE,
                confidence=0.95,
                explanation="Programming task detected.",
                estimated_latency=3.0,
                estimated_cost=0.03,
            )

        # Very complex reasoning
        if complexity.level.value == "very_complex":
            return StrategyDecision(
                strategy=ExecutionStrategy.MULTI_AGENT,
                confidence=0.90,
                explanation="Complex multi-step reasoning.",
                estimated_latency=8.0,
                estimated_cost=0.10,
            )

        # Multi-hop retrieval
        if complexity.requires_multi_hop:
            return StrategyDecision(
                strategy=ExecutionStrategy.RESEARCH,
                confidence=0.90,
                explanation="Multi-stage retrieval required.",
                estimated_latency=6.0,
                estimated_cost=0.05,
            )

        # RAG
        if retrieval_plan.mode.value in {
            "vector",
            "graph",
            "hybrid",
            "multi_stage",
        }:
            return StrategyDecision(
                strategy=ExecutionStrategy.RAG,
                confidence=0.90,
                explanation="Knowledge retrieval required.",
                estimated_latency=2.5,
                estimated_cost=0.02,
            )

        # Default
        return StrategyDecision(
            strategy=ExecutionStrategy.DIRECT,
            confidence=0.80,
            explanation="Simple LLM response.",
            estimated_latency=1.0,
            estimated_cost=0.01,
        )