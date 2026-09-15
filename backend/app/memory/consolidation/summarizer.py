"""
Memory summarization.
"""

from __future__ import annotations

from typing import Iterable, List

from app.memory.models.memory import Memory


class MemorySummarizer:
    """
    Creates compact summaries of related memories.
    """

    def summarize(
        self,
        memories: Iterable[Memory],
        max_sentences: int = 5,
    ) -> str:
        """
        Very simple extractive summarizer.

        Later this can be replaced with an LLM.
        """

        texts = []

        for memory in memories:
            texts.extend(
                sentence.strip()
                for sentence in memory.content.split(".")
                if sentence.strip()
            )

        return ". ".join(texts[:max_sentences]) + (
            "." if texts else ""
        )

    def summarize_memory(
        self,
        memories: List[Memory],
    ) -> Memory:
        """
        Produce a summarized memory.
        """

        if not memories:
            raise ValueError("No memories provided.")

        base = memories[0].model_copy(deep=True)

        base.content = self.summarize(memories)

        base.metadata["summarized"] = True
        base.metadata["source_count"] = len(memories)

        return base