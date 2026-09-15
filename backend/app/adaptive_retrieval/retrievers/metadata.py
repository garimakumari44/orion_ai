"""
Metadata Retriever

Performs structured filtering using document/chunk metadata.

Examples:
- author == "John"
- source == "github"
- language == "en"
- tags contains "python"
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.knowledge_system.models.chunk  import Chunk


class MetadataRetriever:
    """
    Metadata-based retrieval.
    """

    def __init__(self):
        pass

    def retrieve(
        self,
        chunks: List[Chunk],
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Apply metadata filters.
        """

        if not filters:
            return chunks

        results = []

        for chunk in chunks:

            metadata = getattr(chunk, "metadata", {}) or {}

            matched = True

            for key, expected in filters.items():

                value = metadata.get(key)

                if isinstance(expected, list):

                    if value not in expected:
                        matched = False
                        break

                else:

                    if value != expected:
                        matched = False
                        break

            if matched:
                results.append(chunk)

        return results

    def retrieve_by_tag(
        self,
        chunks: List[Chunk],
        tag: str,
    ) -> List[Chunk]:

        results = []

        for chunk in chunks:

            tags = chunk.metadata.get("tags", [])

            if tag in tags:
                results.append(chunk)

        return results

    def retrieve_by_author(
        self,
        chunks: List[Chunk],
        author: str,
    ) -> List[Chunk]:

        return [
            c
            for c in chunks
            if c.metadata.get("author") == author
        ]