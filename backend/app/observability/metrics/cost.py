# metrics/cost.py

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ModelPricing:
    """
    Pricing information for an LLM model.

    Values:
    cost per 1K tokens
    """

    input_cost_per_1k: float

    output_cost_per_1k: float



@dataclass
class CostMetric:
    """
    Represents cost of a single request.
    """

    model: str

    input_tokens: int

    output_tokens: int

    input_cost: float

    output_cost: float

    total_cost: float

    metadata: Dict = field(
        default_factory=dict
    )



class CostTracker:
    """
    Tracks LLM spending.

    Supports:
    - OpenAI
    - Anthropic
    - Gemini
    - OpenRouter
    - Local models
    """

    def __init__(self):

        self.pricing = {

            "gpt-4o": ModelPricing(
                input_cost_per_1k=0.0025,
                output_cost_per_1k=0.010
            ),

            "claude-3.5-sonnet": ModelPricing(
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015
            ),

            "llama-3.3-70b": ModelPricing(
                input_cost_per_1k=0.0008,
                output_cost_per_1k=0.0008
            )
        }


        self.history = []



    def add_model(
        self,
        model: str,
        input_cost_per_1k: float,
        output_cost_per_1k: float
    ):

        self.pricing[model] = ModelPricing(
            input_cost_per_1k=input_cost_per_1k,
            output_cost_per_1k=output_cost_per_1k
        )



    def calculate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict] = None
    ):


        if model not in self.pricing:
            raise ValueError(
                f"Unknown model pricing: {model}"
            )


        price = self.pricing[model]


        input_cost = (
            input_tokens / 1000
        ) * price.input_cost_per_1k


        output_cost = (
            output_tokens / 1000
        ) * price.output_cost_per_1k



        metric = CostMetric(

            model=model,

            input_tokens=input_tokens,

            output_tokens=output_tokens,

            input_cost=round(
                input_cost,
                6
            ),

            output_cost=round(
                output_cost,
                6
            ),

            total_cost=round(
                input_cost + output_cost,
                6
            ),

            metadata=metadata or {}
        )


        self.history.append(metric)


        return metric



    def total_cost(self):

        return round(
            sum(
                item.total_cost
                for item in self.history
            ),
            6
        )



    def breakdown(self):

        result = {}

        for item in self.history:

            result.setdefault(
                item.model,
                0
            )

            result[item.model] += (
                item.total_cost
            )


        return result