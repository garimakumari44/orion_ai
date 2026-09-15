from enum import Enum
from dataclasses import dataclass
from typing import List, Dict


class RepairStrategy(str, Enum):
    """
    Possible repair actions.
    """

    NONE = "none"

    REWRITE = "rewrite"

    FACT_CHECK = "fact_check"

    ADD_CITATIONS = "add_citations"

    IMPROVE_REASONING = "improve_reasoning"

    FIX_FORMATTING = "fix_formatting"

    REMOVE_HALLUCINATION = "remove_hallucination"

    REGENERATE = "regenerate"



@dataclass
class RepairPlan:
    """
    Final repair decision.
    """

    strategies: List[RepairStrategy]

    severity: str

    explanation: str



class RepairPlanner:
    """
    Decides how an answer should be repaired
    based on evaluation failures.
    """

    def __init__(
        self,
        thresholds=None
    ):

        self.thresholds = thresholds or {
            "critical": 0.4,
            "warning": 0.7
        }


    def create_plan(
        self,
        scores: Dict[str, float],
        issues: List[str]
    ) -> RepairPlan:


        strategies = []


        # factual failures
        if scores.get(
            "factual",
            1
        ) < self.thresholds["critical"]:

            strategies.append(
                RepairStrategy.FACT_CHECK
            )

            strategies.append(
                RepairStrategy.REWRITE
            )


        # hallucination detection
        if scores.get(
            "hallucination",
            1
        ) < self.thresholds["critical"]:

            strategies.append(
                RepairStrategy.REMOVE_HALLUCINATION
            )


        # citation failures
        if scores.get(
            "citation",
            1
        ) < self.thresholds["warning"]:

            strategies.append(
                RepairStrategy.ADD_CITATIONS
            )


        # reasoning failures
        if scores.get(
            "reasoning",
            1
        ) < self.thresholds["warning"]:

            strategies.append(
                RepairStrategy.IMPROVE_REASONING
            )


        # formatting problems
        if scores.get(
            "formatting",
            1
        ) < self.thresholds["warning"]:

            strategies.append(
                RepairStrategy.FIX_FORMATTING
            )


        # determine severity

        if len(strategies) >= 3:
            severity = "high"

        elif len(strategies) > 0:
            severity = "medium"

        else:
            severity = "low"



        if not strategies:
            strategies.append(
                RepairStrategy.NONE
            )


        explanation = (
            f"Detected {len(issues)} issues. "
            f"Selected repair actions: "
            f"{', '.join(strategies)}"
        )


        return RepairPlan(
            strategies=strategies,
            severity=severity,
            explanation=explanation
        )