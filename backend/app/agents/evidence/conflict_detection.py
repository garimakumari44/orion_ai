"""
Conflict Detection Engine

Detects contradictions between
research claims and evidence sources.
"""

from typing import Dict, Any, List



class ConflictDetector:
    """
    Finds conflicting information.

    Examples:
    - Different revenue numbers
    - Contradictory management statements
    - Conflicting market data
    """



    def __init__(self):

        self.conflict_threshold = 0.5



    async def detect(
        self,
        evidence_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        conflicts = []


        for index, item in enumerate(evidence_items):

            for compare_item in evidence_items[index + 1:]:

                result = self.compare(
                    item,
                    compare_item
                )


                if result["conflict"]:

                    conflicts.append(
                        result
                    )


        return {

            "total_conflicts":
                len(conflicts),

            "conflicts":
                conflicts,

            "status":
                "review_required"
                if conflicts
                else
                "clean"

        }




    def compare(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> Dict[str, Any]:

        first_claim = str(
            first.get(
                "claim",
                ""
            )
        ).lower()


        second_claim = str(
            second.get(
                "claim",
                ""
            )
        ).lower()



        conflict = False


        if (
            first.get("value")
            and
            second.get("value")
        ):

            if (
                first["value"]
                !=
                second["value"]
            ):
                conflict = True



        return {

            "claim_1":
                first_claim,

            "claim_2":
                second_claim,

            "conflict":
                conflict,

            "severity":
                "high"
                if conflict
                else "none"

        }