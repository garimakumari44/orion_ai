"""
HyDE Generator

Hypothetical Document Embeddings.

Reference:
Precise Zero-Shot Dense Retrieval without Relevance Labels
(Gao et al., 2022)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


# ===============================
# Models
# ===============================

@dataclass(slots=True)
class HyDERequest:

    query: str
    max_tokens: int = 512



@dataclass(slots=True)
class HyDEResult:

    query: str
    hypothetical_document: str



# ===============================
# LLM Interface
# ===============================

class LLMGenerator(Protocol):

    async def generate(
        self,
        prompt: str,
        max_tokens: int,
    ) -> str:
        ...



# ===============================
# Prompt
# ===============================

class HyDEPromptBuilder:


    @staticmethod
    def build(
        query: str
    ) -> str:

        return f"""

Create a factual technical document
answering this search query.

Query:
{query}

Requirements:

- Explain concepts clearly
- Include examples
- Include technical details
- Avoid speculation

Document:
"""



# ===============================
# Generator
# ===============================

class HyDEGenerator:


    def __init__(
        self,
        llm: LLMGenerator | None = None,
    ):

        self.llm = llm



    async def generate(
        self,
        request: HyDERequest,
    ) -> HyDEResult:


        if self.llm:

            prompt = (
                HyDEPromptBuilder.build(
                    request.query
                )
            )


            document = await self.llm.generate(
                prompt,
                request.max_tokens
            )

        else:

            document = (
                "A technical document explaining "
                f"{request.query} with concepts, "
                "examples and implementation details."
            )


        return HyDEResult(
            query=request.query,
            hypothetical_document=document,
        )