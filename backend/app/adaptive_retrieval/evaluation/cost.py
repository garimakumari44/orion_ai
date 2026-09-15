from dataclasses import dataclass
from typing import Dict



@dataclass
class ModelPricing:
    """
    Model pricing per 1K tokens.
    """

    input_cost: float
    output_cost: float



class CostTracker:
    """
    Tracks AI system cost.
    """


    def __init__(
        self,
        pricing: ModelPricing
    ):

        self.pricing = pricing

        self.total_input_tokens = 0
        self.total_output_tokens = 0



    def add_usage(
        self,
        input_tokens: int,
        output_tokens: int
    ):

        self.total_input_tokens += (
            input_tokens
        )

        self.total_output_tokens += (
            output_tokens
        )



    def calculate_cost(self) -> Dict:

        input_cost = (
            self.total_input_tokens
            /
            1000
            *
            self.pricing.input_cost
        )


        output_cost = (
            self.total_output_tokens
            /
            1000
            *
            self.pricing.output_cost
        )


        return {

            "input_tokens":
                self.total_input_tokens,

            "output_tokens":
                self.total_output_tokens,

            "input_cost":
                input_cost,

            "output_cost":
                output_cost,

            "total_cost":
                input_cost + output_cost
        }