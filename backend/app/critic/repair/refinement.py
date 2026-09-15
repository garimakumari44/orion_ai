"""
refinement.py

Response refinement module.

Responsible for:
- improving response quality
- iterative polishing
- applying evaluator feedback

Used after:
- rewrite.py
- regenerate.py
"""


from dataclasses import dataclass
from typing import List, Optional, Any



@dataclass
class RefinementRequest:
    """
    Input for refinement.
    """

    response: str

    issues: List[str]

    iteration: int = 1



@dataclass
class RefinementResult:
    """
    Refined response output.
    """

    response: str

    improvements: List[str]

    iterations: int



class RefinementEngine:
    """
    Improves an existing response.

    Unlike regeneration:
    - preserves useful information
    - makes targeted improvements
    """


    def __init__(
        self,
        llm_client: Any = None,
        max_iterations: int = 3
    ):

        self.llm_client = llm_client

        self.max_iterations = max_iterations



    def refine(
        self,
        request: RefinementRequest
    ) -> RefinementResult:


        current_response = (
            request.response
        )


        improvements = []


        for iteration in range(
            self.max_iterations
        ):


            current_response, changes = (
                self._refine_once(
                    current_response,
                    request.issues
                )
            )


            improvements.extend(
                changes
            )


        return RefinementResult(

            response=current_response,

            improvements=improvements,

            iterations=self.max_iterations

        )



    def _refine_once(
        self,
        response: str,
        issues: List[str]
    ):


        if self.llm_client:


            prompt = self._build_prompt(
                response,
                issues
            )


            improved = (
                self.llm_client.generate(
                    prompt
                )
            )


            return improved, [
                "LLM refinement applied"
            ]



        # Rule based fallback

        changes = []

        refined = response


        for issue in issues:


            issue_lower = (
                issue.lower()
            )


            if "clarity" in issue_lower:

                refined = (
                    refined.strip()
                )

                changes.append(
                    "Improved clarity"
                )


            if "format" in issue_lower:

                refined = (
                    self._format_response(
                        refined
                    )
                )

                changes.append(
                    "Improved formatting"
                )


            if "redundant" in issue_lower:

                refined = (
                    self._remove_duplicates(
                        refined
                    )
                )

                changes.append(
                    "Removed redundancy"
                )


        return refined, changes



    def _build_prompt(
        self,
        response: str,
        issues: List[str]
    ):


        return f"""
You are a response refinement agent.

Improve this response:

{response}


Issues:

{issues}


Goals:

- Improve clarity
- Improve structure
- Preserve factual information
- Remove unnecessary repetition
- Make reasoning easier to follow

Return only the improved response.
"""



    def _format_response(
        self,
        response: str
    ):

        return response.replace(
            "\n\n\n",
            "\n\n"
        )



    def _remove_duplicates(
        self,
        response: str
    ):


        lines = response.split(
            "\n"
        )


        seen = set()

        result = []


        for line in lines:

            if line not in seen:

                result.append(line)

                seen.add(line)


        return "\n".join(result)