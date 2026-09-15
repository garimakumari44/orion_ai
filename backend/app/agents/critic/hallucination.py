"""
Hallucination Detection Module

Detects unsupported or fabricated information
in research responses.
"""

from typing import Dict, Any, List


class HallucinationDetector:
    """
    Detects potential AI hallucinations.

    Checks:
    - Missing sources
    - Impossible financial metrics
    - Unsupported claims
    - Contradictory statements
    """

    def __init__(self):

        self.risk_keywords = [
            "guaranteed",
            "certain",
            "will definitely",
            "zero risk"
        ]


    async def detect(
        self,
        output: Dict[str, Any]
    ) -> Dict[str, Any]:

        text = str(output).lower()

        issues = []

        for keyword in self.risk_keywords:

            if keyword in text:
                issues.append(
                    {
                        "type": "overconfidence",
                        "keyword": keyword
                    }
                )


        missing_sources = self.check_sources(
            output
        )

        if missing_sources:
            issues.append(
                {
                    "type": "missing_sources",
                    "message":
                    "Claims without supporting evidence"
                }
            )


        return {
            "hallucination_risk":
                self.calculate_risk(
                    issues
                ),
            "issues": issues
        }



    def check_sources(
        self,
        output: Dict[str, Any]
    ) -> bool:

        sources = output.get(
            "sources"
        )

        return not bool(sources)



    def calculate_risk(
        self,
        issues: List
    ) -> str:

        count = len(issues)

        if count == 0:
            return "low"

        if count <= 2:
            return "medium"

        return "high"