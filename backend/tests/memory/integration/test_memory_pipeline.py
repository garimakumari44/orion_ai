"""
Integration test for the complete memory pipeline.

Pipeline

Conversation
        ↓
Extractors
        ↓
Working / Semantic Stores
        ↓
Searcher
        ↓
Ranker
        ↓
Context Builder
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest


from app.memory.extractors.conversation import ConversationExtractor
from app.memory.extractors.preference import PreferenceExtractor
from app.memory.retrieval.context import ContextBuilder
from app.memory.retrieval.ranking import MemoryRanker
from app.memory.retrieval.search import MemorySearcher
from app.memory.stores.semantic import SemanticMemoryStore
from app.memory.stores.working import WorkingMemoryStore


# ----------------------------------------------------------------------
# Fake vector store
# ----------------------------------------------------------------------

class FakeVectorStore:
    """
    Minimal vector search backend used by MemorySearcher.
    """

    def __init__(self, memories):
        self.memories = memories

    def search(self, query: str, top_k: int):
        query = query.lower()

        results = []

        for memory in self.memories:

            text = ""

            if hasattr(memory, "content"):

                if isinstance(memory.content, str):
                    text = memory.content

                elif hasattr(memory.content, "text"):
                    text = memory.content.text or ""

                elif hasattr(memory.content, "summary"):
                    text = memory.content.summary or ""

            if query in text.lower():

                memory.similarity = 0.95

                results.append(memory)

        return results[:top_k]


# ----------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------

def test_memory_pipeline():

    messages = [
        {
            "role": "user",
            "content": "I prefer Python for backend development."
        },
        {
            "role": "assistant",
            "content": "Great choice."
        },
        {
            "role": "user",
            "content": "I am building an AI research platform."
        },
    ]

    # ----------------------------------------------------------
    # Extraction
    # ----------------------------------------------------------

    conversation_extractor = ConversationExtractor()
    preference_extractor = PreferenceExtractor()

    conversation_memories = conversation_extractor.extract(messages)
    preference_memories = preference_extractor.extract(messages)

    memories = conversation_memories + preference_memories

    assert memories
    assert len(memories) >= 2

    # ----------------------------------------------------------
    # Stores
    # ----------------------------------------------------------

    working_store = WorkingMemoryStore(capacity=20)
    semantic_store = SemanticMemoryStore()

    for memory in memories:

        working_store.add(memory)

        # semantic store expects id
        if getattr(memory, "id", None):
            semantic_store.add(memory)

    assert len(working_store) == len(memories)

    # ----------------------------------------------------------
    # Retrieval
    # ----------------------------------------------------------

    searcher = MemorySearcher(
        vector_store=FakeVectorStore(working_store.get_all())
    )

    result = searcher.search(
        "python",
        top_k=5,
        use_keyword=False,
        use_graph=False,
    )

    assert result.count >= 1

    # ----------------------------------------------------------
    # Ranking
    # ----------------------------------------------------------

    now = datetime.now(timezone.utc)

    for memory in result.memories:

          memory.importance = 0.8
          memory.confidence = 1.0
          memory.access_count = 10
          memory.boost = 0.0

    ranked = MemoryRanker().rank(result.memories)

    assert ranked

    assert ranked[0].ranking_score >= ranked[-1].ranking_score

    # ----------------------------------------------------------
    # Context
    # ----------------------------------------------------------

    builder = ContextBuilder(max_memories=5)

    context = builder.build(
        query="python",
        memories=ranked,
    )

    assert context.query == "python"

    assert context.count == len(ranked)

    assert context.memories == ranked

    context_dict = context.to_dict()

    assert context_dict["query"] == "python"

    assert context_dict["count"] == len(ranked)