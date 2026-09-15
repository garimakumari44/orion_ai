"""
Context Builder

Creates the final LLM context from retrieved
knowledge, memory, and supporting documents.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ContextBuilder:
    """
    Builds the final context supplied to the LLM.

    Responsibilities
    ----------------
    • Prioritize memory
    • Organize documents by source
    • Respect token budget
    • Preserve metadata
    """

    def __init__(
        self,
        max_tokens: int =3000,
    ):
        self.max_tokens = max_tokens

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def build(
        self,
        documents: List[Dict[str, Any]],
    ) -> str:

        memory_docs = []
        knowledge_docs = []

        for doc in documents:

            if doc.get("retriever") == "memory":
                memory_docs.append(doc)
            else:
                knowledge_docs.append(doc)

        sections = []

        memory_section = self._build_section(
            "Relevant Memory",
            memory_docs,
        )

        if memory_section:
            sections.append(memory_section)

        knowledge_section = self._build_section(
            "Knowledge",
            knowledge_docs,
        )

        if knowledge_section:
            sections.append(knowledge_section)

        return "\n\n".join(sections)

    def build_with_metadata(
        self,
        documents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        return {
            "context": self.build(documents),
            "sources": [
                {
                    "source": doc.get("source"),
                    "retriever": doc.get("retriever"),
                    "score": doc.get("score"),
                    "memory_type": doc.get("memory_type"),
                }
                for doc in documents
            ],
            "document_count": len(documents),
            "memory_count": sum(
                1
                for d in documents
                if d.get("retriever") == "memory"
            ),
        }

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    def _build_section(
        self,
        title: str,
        docs: List[Dict[str, Any]],
    ) -> str:

        if not docs:
            return ""

        parts = [f"## {title}"]

        token_count = 0

        for doc in docs:

            text = doc.get("text", "").strip()

            if not text:
                continue

            tokens = len(text.split())

            if token_count + tokens > self.max_tokens:
                break

            source = doc.get("source", "Unknown")

            score = doc.get("score")

            header = f"[Source: {source}"

            if score is not None:
                header += f" | Score: {score:.3f}"

            memory_type = doc.get("memory_type")

            if memory_type:
                header += f" | {memory_type}"

            header += "]"

            parts.append(header)
            parts.append(text)

            token_count += tokens

        return "\n".join(parts)