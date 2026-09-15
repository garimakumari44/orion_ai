"""
LLM-based Critic.

Uses an LLM to review evaluator outputs and provide
high-level critique, strengths, weaknesses, and recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class LLMCritique:
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    confidence: float


class LLMCritic:
    """
    Abstract LLM critic.

    Integrate with OpenAI, Anthropic, Ollama,
    Azure OpenAI, etc.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        self.client = llm_client

    def build_prompt(
        self,
        question: str,
        answer: str,
        evaluator_results: Dict[str, Any],
    ) -> str:
        return f"""
You are an expert AI evaluator.

Question:
{question}

Answer:
{answer}

Evaluation Results:
{evaluator_results}

Provide:

1. Summary
2. Strengths
3. Weaknesses
4. Recommendations
5. Confidence (0-1)
"""

    def critique(
        self,
        question: str,
        answer: str,
        evaluator_results: Dict[str, Any],
    ) -> LLMCritique:
        """
        Replace this stub with an actual LLM call.
        """

        _ = self.build_prompt(question, answer, evaluator_results)

        return LLMCritique(
            summary="Overall answer is acceptable.",
            strengths=["Clear structure"],
            weaknesses=["Needs more evidence"],
            recommendations=["Improve citations"],
            confidence=0.82,
        )