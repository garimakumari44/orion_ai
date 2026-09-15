# metrics/tokens.py

from dataclasses import dataclass, field
from typing import Dict



@dataclass
class TokenUsage:

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    metadata: Dict = field(
        default_factory=dict
    )


    def calculate_total(self):

        self.total_tokens = (
            self.prompt_tokens +
            self.completion_tokens
        )

        return self.total_tokens



class TokenTracker:
    """
    Tracks LLM token consumption.

    Used by:
    - OpenAI
    - Anthropic
    - Gemini
    - OpenRouter
    - Local models
    """

    def __init__(self):

        self.history = []



    def record(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        metadata: Dict = None
    ):

        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            metadata=metadata or {}
        )


        usage.calculate_total()


        self.history.append(
            usage
        )


        return usage



    def total_usage(self):

        return {

            "prompt_tokens":
                sum(
                    x.prompt_tokens
                    for x in self.history
                ),


            "completion_tokens":
                sum(
                    x.completion_tokens
                    for x in self.history
                ),


            "total_tokens":
                sum(
                    x.total_tokens
                    for x in self.history
                )
        }



    def latest(self):

        if not self.history:
            return None

        return self.history[-1]