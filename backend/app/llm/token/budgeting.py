"""
Context budgeting.

Splits model context window between:

- System prompt
- Conversation
- Retrieved documents
- Tool output
- Response

Used by planner, retrieval, memory and LLM manager.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Budget:

    total: int

    system: int

    conversation: int

    retrieval: int

    tools: int

    response: int

    @property
    def prompt(self) -> int:
        return (
            self.system
            + self.conversation
            + self.retrieval
            + self.tools
        )


class TokenBudgeter:
    """
    Creates token budgets.

    Default strategy:

    10% system
    35% conversation
    30% retrieval
    10% tools
    15% response
    """

    def __init__(
        self,
        context_window: int,
    ):
        self.context_window = context_window

    # ---------------------------------------------------------

    def allocate(self) -> Budget:

        total = self.context_window

        system = int(total * 0.10)

        conversation = int(total * 0.35)

        retrieval = int(total * 0.30)

        tools = int(total * 0.10)

        response = (
            total
            - system
            - conversation
            - retrieval
            - tools
        )

        return Budget(
            total=total,
            system=system,
            conversation=conversation,
            retrieval=retrieval,
            tools=tools,
            response=response,
        )

    # ---------------------------------------------------------

    def custom(
        self,
        *,
        system: float,
        conversation: float,
        retrieval: float,
        tools: float,
        response: float,
    ) -> Budget:

        total = self.context_window

        values = [
            system,
            conversation,
            retrieval,
            tools,
            response,
        ]

        if abs(sum(values) - 1.0) > 0.001:
            raise ValueError("Ratios must sum to 1.")

        return Budget(
            total=total,
            system=int(total * system),
            conversation=int(total * conversation),
            retrieval=int(total * retrieval),
            tools=int(total * tools),
            response=int(total * response),
        )

    # ---------------------------------------------------------

    def available_response_tokens(
        self,
        used_prompt_tokens: int,
    ) -> int:
        """
        Remaining response capacity.
        """

        return max(
            0,
            self.context_window - used_prompt_tokens,
        )

    def exceeds_limit(
        self,
        prompt_tokens: int,
    ) -> bool:
        """
        Check context overflow.
        """
        return prompt_tokens >= self.context_window

    def utilization(
        self,
        used: int,
    ) -> float:
        """
        Percentage utilization.
        """

        return used / self.context_window