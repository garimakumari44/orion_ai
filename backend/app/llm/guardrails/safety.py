"""
Prompt safety checks.

Responsible for:

- Prompt injection detection
- Jailbreak detection
- System prompt protection
- Unsafe instruction detection
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class SafetyResult:
    safe: bool
    score: float
    violations: List[str]


class PromptSafety:

    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"forget your instructions",
        r"system prompt",
        r"developer message",
        r"reveal hidden prompt",
        r"print your prompt",
        r"override safety",
        r"disable guardrails",
    ]

    JAILBREAK_PATTERNS = [
        r"act as dan",
        r"jailbreak",
        r"do anything now",
        r"evil assistant",
        r"pretend there are no rules",
    ]

    TOOL_PATTERNS = [
        r"call internal api",
        r"execute shell",
        r"run terminal",
        r"access filesystem",
        r"read secrets",
        r"export environment",
    ]

    def evaluate(self, prompt: str) -> SafetyResult:
        """
        Evaluate prompt safety.
        """

        text = prompt.lower()

        violations = []

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text):
                violations.append("prompt_injection")

        for pattern in self.JAILBREAK_PATTERNS:
            if re.search(pattern, text):
                violations.append("jailbreak")

        for pattern in self.TOOL_PATTERNS:
            if re.search(pattern, text):
                violations.append("unsafe_tool_request")

        score = max(0.0, 1.0 - len(violations) * 0.3)

        return SafetyResult(
            safe=len(violations) == 0,
            score=score,
            violations=sorted(set(violations)),
        )


class SafetyGuard:
    """
    High-level safety wrapper.
    """

    def __init__(self):
        self.prompt_checker = PromptSafety()

    def check_prompt(self, prompt: str) -> SafetyResult:
        return self.prompt_checker.evaluate(prompt)