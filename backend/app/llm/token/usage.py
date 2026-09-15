"""
Token usage tracking.

Tracks:
- Prompt tokens
- Completion tokens
- Total tokens
- Requests
- Cost
- Latency

Can aggregate usage across:
- Request
- Session
- User
- Provider
- Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from typing import Dict, Optional


@dataclass(slots=True)
class TokenUsage:
    """
    Usage information for a single LLM request.
    """

    provider: str
    model: str

    prompt_tokens: int = 0
    completion_tokens: int = 0

    latency: float = 0.0
    cost: float = 0.0

    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class UsageTracker:
    """
    Tracks token usage during runtime.
    """

    def __init__(self):

        self.records: list[TokenUsage] = []

        self.by_model = defaultdict(int)

        self.by_provider = defaultdict(int)

        self.total_prompt = 0

        self.total_completion = 0

        self.total_cost = 0.0

        self.total_requests = 0

    # -----------------------------------------------------

    def add(self, usage: TokenUsage):

        self.records.append(usage)

        self.total_requests += 1

        self.total_prompt += usage.prompt_tokens

        self.total_completion += usage.completion_tokens

        self.total_cost += usage.cost

        self.by_model[usage.model] += usage.total_tokens

        self.by_provider[usage.provider] += usage.total_tokens

    # -----------------------------------------------------

    @property
    def total_tokens(self):

        return self.total_prompt + self.total_completion

    @property
    def average_tokens(self):

        if self.total_requests == 0:
            return 0

        return self.total_tokens / self.total_requests

    @property
    def average_cost(self):

        if self.total_requests == 0:
            return 0

        return self.total_cost / self.total_requests

    @property
    def average_latency(self):

        if not self.records:
            return 0

        return sum(r.latency for r in self.records) / len(self.records)

    # -----------------------------------------------------

    def provider_summary(self):

        return dict(self.by_provider)

    def model_summary(self):

        return dict(self.by_model)

    # -----------------------------------------------------

    def summary(self):

        return {
            "requests": self.total_requests,
            "prompt_tokens": self.total_prompt,
            "completion_tokens": self.total_completion,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 6),
            "average_tokens": round(self.average_tokens, 2),
            "average_cost": round(self.average_cost, 6),
            "average_latency": round(self.average_latency, 3),
        }

    # -----------------------------------------------------

    def reset(self):

        self.records.clear()

        self.by_model.clear()

        self.by_provider.clear()

        self.total_prompt = 0

        self.total_completion = 0

        self.total_cost = 0.0

        self.total_requests = 0


usage_tracker = UsageTracker()