"""
regenerate.py

Full response regeneration.

Used when:
- Rewrite is insufficient
- Severe hallucination
- Logical failure
- Unsafe response
"""


from dataclasses import dataclass
from typing import Optional, List, Any



@dataclass
class RegenerationRequest:

    original_response: str

    problem: List[str]

    context: Optional[str] = None



@dataclass
class RegeneratedResponse:

    response: str

    model: str

    repaired: bool = True



class ResponseRegenerator:
    """
    Completely regenerate
    an answer using feedback.
    """



    def __init__(
        self,
        llm_client: Any = None,
        model: str = "default"
    ):

        self.llm_client = llm_client

        self.model = model



    def regenerate(
        self,
        request: RegenerationRequest
    ) -> RegeneratedResponse:


        prompt = self._create_prompt(
            request
        )


        if self.llm_client:


            response = (
                self.llm_client.generate(
                    prompt
                )
            )


        else:

            response = (
                "Regenerated response placeholder.\n\n"
                + request.original_response
            )



        return RegeneratedResponse(

            response=response,

            model=self.model

        )



    def _create_prompt(
        self,
        request: RegenerationRequest
    ):


        return f"""
You are an expert response regeneration system.

The previous answer failed evaluation.

Original answer:

{request.original_response}


Problems detected:

{request.problem}


Additional context:

{request.context}


Generate a completely new answer.

Rules:

- Do not repeat incorrect information
- Use evidence when available
- Improve reasoning
- Be concise and accurate
"""