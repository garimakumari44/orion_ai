"""
Context Citation Management

Responsible for:
- Tracking document/chunk citations
- Deduplicating citations
- Formatting citations
- Building provenance information
- Mapping context back to source documents
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import OrderedDict


# ============================================================
# Citation
# ============================================================

@dataclass(slots=True)
class Citation:
    """
    Citation for a retrieved chunk.
    """

    document_id: str
    chunk_id: str

    source: str
    title: Optional[str] = None

    page: Optional[int] = None
    section: Optional[str] = None

    score: float = 0.0

    metadata: Dict = field(default_factory=dict)


# ============================================================
# Provenance Record
# ============================================================

@dataclass(slots=True)
class ProvenanceRecord:
    """
    Provenance information for generated responses.
    """

    response_span: str

    citation: Citation

    confidence: float


# ============================================================
# Citation Formatter
# ============================================================

class CitationFormatter:
    """
    Converts citations into readable strings.
    """

    def format(self, citation: Citation) -> str:
        parts = []

        if citation.title:
            parts.append(citation.title)

        if citation.page is not None:
            parts.append(f"p.{citation.page}")

        if citation.section:
            parts.append(citation.section)

        if citation.source:
            parts.append(citation.source)

        return " | ".join(parts)

    def format_many(self, citations: List[Citation]) -> List[str]:
        return [self.format(c) for c in citations]


# ============================================================
# Citation Manager
# ============================================================

class CitationManager:
    """
    Maintains unique citations across the context.
    """

    def __init__(self):
        self._citations: OrderedDict[str, Citation] = OrderedDict()

    def _key(self, citation: Citation) -> str:
        return f"{citation.document_id}:{citation.chunk_id}"

    def add(self, citation: Citation):

        self._citations[self._key(citation)] = citation

    def add_many(self, citations: List[Citation]):

        for citation in citations:
            self.add(citation)

    def get_all(self) -> List[Citation]:

        return list(self._citations.values())

    def clear(self):

        self._citations.clear()

    def count(self) -> int:
        return len(self._citations)


# ============================================================
# Citation Resolver
# ============================================================

class CitationResolver:
    """
    Maps generated text to citations.
    """

    def __init__(self):

        self.records: List[ProvenanceRecord] = []

    def attach(
        self,
        response_span: str,
        citation: Citation,
        confidence: float = 1.0,
    ):

        self.records.append(
            ProvenanceRecord(
                response_span=response_span,
                citation=citation,
                confidence=confidence,
            )
        )

    def resolve(self, response_span: str) -> List[ProvenanceRecord]:

        return [
            r
            for r in self.records
            if r.response_span == response_span
        ]

    def clear(self):
        self.records.clear()


# ============================================================
# Citation Builder
# ============================================================

class CitationBuilder:
    """
    Builds citations directly from retrieved chunks.
    """

    @staticmethod
    def from_chunk(chunk) -> Citation:
        """
        Expected chunk interface:

        chunk.document_id
        chunk.chunk_id
        chunk.metadata
        chunk.score
        """

        metadata = getattr(chunk, "metadata", {}) or {}

        return Citation(
            document_id=chunk.document_id,
            chunk_id=chunk.chunk_id,
            source=metadata.get("source", ""),
            title=metadata.get("title"),
            page=metadata.get("page"),
            section=metadata.get("section"),
            score=getattr(chunk, "score", 0.0),
            metadata=metadata,
        )

    @staticmethod
    def from_chunks(chunks) -> List[Citation]:

        return [
            CitationBuilder.from_chunk(chunk)
            for chunk in chunks
        ]


# ============================================================
# Citation Index
# ============================================================

class CitationIndex:
    """
    Fast lookup by document/chunk.
    """

    def __init__(self):

        self.by_document: Dict[str, List[Citation]] = {}

        self.by_chunk: Dict[str, Citation] = {}

    def add(self, citation: Citation):

        self.by_chunk[citation.chunk_id] = citation

        self.by_document.setdefault(
            citation.document_id,
            [],
        ).append(citation)

    def get_chunk(self, chunk_id: str) -> Optional[Citation]:

        return self.by_chunk.get(chunk_id)

    def get_document(self, document_id: str) -> List[Citation]:

        return self.by_document.get(document_id, [])


# ============================================================
# Citation Statistics
# ============================================================

class CitationStatistics:
    """
    Computes citation statistics.
    """

    @staticmethod
    def documents(citations: List[Citation]) -> int:

        return len(
            {
                c.document_id
                for c in citations
            }
        )

    @staticmethod
    def average_score(citations: List[Citation]) -> float:

        if not citations:
            return 0.0

        return sum(c.score for c in citations) / len(citations)

    @staticmethod
    def top_sources(citations: List[Citation]) -> Dict[str, int]:

        stats: Dict[str, int] = {}

        for citation in citations:
            stats[citation.source] = (
                stats.get(citation.source, 0) + 1
            )

        return stats