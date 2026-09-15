"""
LLM pricing utilities.

Stores model pricing and estimates
request cost.

Prices are expressed in USD per
1 million tokens.
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------
# Pricing Model
# ---------------------------------------------------------


@dataclass(slots=True)
class ModelPricing:

    input_per_million: float

    output_per_million: float


# ---------------------------------------------------------
# Registry
# ---------------------------------------------------------


PRICING = {

    # OpenAI

    "gpt-4.1": ModelPricing(
        input_per_million=2.00,
        output_per_million=8.00,
    ),

    "gpt-4.1-mini": ModelPricing(
        input_per_million=0.40,
        output_per_million=1.60,
    ),

    "gpt-4o": ModelPricing(
        input_per_million=2.50,
        output_per_million=10.00,
    ),

    "gpt-4o-mini": ModelPricing(
        input_per_million=0.15,
        output_per_million=0.60,
    ),

    # Anthropic

    "claude-4-sonnet": ModelPricing(
        input_per_million=3.00,
        output_per_million=15.00,
    ),

    # Gemini

    "gemini-2.5-pro": ModelPricing(
        input_per_million=1.25,
        output_per_million=10.00,
    ),

    "gemini-2.5-flash": ModelPricing(
        input_per_million=0.30,
        output_per_million=2.50,
    ),
}


# ---------------------------------------------------------
# Calculator
# ---------------------------------------------------------


class PricingCalculator:

    def __init__(self):

        self.pricing = PRICING

    # -----------------------------------------------------

    def has_model(self, model: str):

        return model in self.pricing

    # -----------------------------------------------------

    def estimate(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:

        if model not in self.pricing:
            return 0.0

        p = self.pricing[model]

        input_cost = (
            prompt_tokens
            / 1_000_000
        ) * p.input_per_million

        output_cost = (
            completion_tokens
            / 1_000_000
        ) * p.output_per_million

        return input_cost + output_cost

    # -----------------------------------------------------

    def estimate_from_total(
        self,
        model: str,
        total_tokens: int,
    ) -> float:

        return self.estimate(
            model,
            total_tokens,
            0,
        )

    # -----------------------------------------------------

    def add_model(
        self,
        model: str,
        input_price: float,
        output_price: float,
    ):

        self.pricing[model] = ModelPricing(
            input_per_million=input_price,
            output_per_million=output_price,
        )

    # -----------------------------------------------------

    def remove_model(self, model: str):

        self.pricing.pop(model, None)

    # -----------------------------------------------------

    def models(self):

        return list(self.pricing.keys())


pricing = PricingCalculator()