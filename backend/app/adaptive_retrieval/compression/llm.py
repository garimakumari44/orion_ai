"""
LLM-powered compression.

Uses an LLM to remove irrelevant information
while preserving facts required to answer
the user's query.
"""

from __future__ import annotations

from typing import List

from models.chunk import Chunk


class BaseLLM:

    async def generate(
        self,
        prompt: str,
    ) -> str:
        raise NotImplementedError


class LLMCompressor:

    def __init__(
        self,
        llm: BaseLLM,
    ):
        self.llm = llm

    async def compress_chunk(
        self,
        query: str,
        chunk: Chunk,
    ) -> Chunk:

        prompt = f"""
You are a retrieval compression assistant.

User Query:
{query}

Document:
{chunk.text}

Instructions:
- Remove irrelevant information.
- Preserve all facts.
- Keep names, dates, numbers.
- Return only compressed text.
"""

        compressed = await self.llm.generate(prompt)

        new_chunk = chunk.model_copy(deep=True)
        new_chunk.text = compressed.strip()

        return new_chunk

    async def compress(
        self,
        query: str,
        chunks: List[Chunk],
    ) -> List[Chunk]:

        results = []

        for chunk in chunks:
            results.append(
                await self.compress_chunk(
                    query,
                    chunk,
                )
            )

        return results