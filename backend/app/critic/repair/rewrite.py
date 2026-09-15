from typing import List, Dict


class ResponseRewriter:
    """
    Repairs responses using
    evaluation feedback.
    """


    def __init__(
        self,
        llm_client=None
    ):

        self.llm_client = llm_client



    def rewrite(
        self,
        response: str,
        issues: List[str],
        strategy: List[str]
    ) -> str:


        prompt = self._build_prompt(
            response,
            issues,
            strategy
        )


        if self.llm_client:

            return self.llm_client.generate(
                prompt
            )


        # fallback rule based repair

        return self.rule_based_rewrite(
            response,
            issues
        )



    def _build_prompt(
        self,
        response,
        issues,
        strategy
    ):

        return f"""
You are an expert AI response repair system.

Original Response:

{response}


Detected Problems:

{issues}


Repair Strategy:

{strategy}


Rewrite the response.

Requirements:

- remove incorrect claims
- improve reasoning
- add missing evidence
- preserve useful information
- make answer clear
"""



    def rule_based_rewrite(
        self,
        response: str,
        issues: List[str]
    ):


        repaired = response


        if any(
            "citation" in i.lower()
            for i in issues
        ):

            repaired += (
                "\n\nSources should be verified "
                "before relying on these claims."
            )


        if any(
            "hallucination" in i.lower()
            for i in issues
        ):

            repaired = (
                "Verified information only:\n\n"
                + repaired
            )


        return repaired