"""
Provenance models.

Tracks where enriched data originated and how it was
produced. Useful for explainability, auditing, and
knowledge graph lineage.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ProvenanceRecord(BaseModel):
    """
    Records the origin of an enrichment result.
    """

    source_document: str = Field(
        ...,
        description="Original document identifier",
    )

    source_chunk: Optional[str] = Field(
        default=None,
        description="Chunk identifier",
    )

    extractor: str = Field(
        ...,
        description="Extractor or model name",
    )

    version: str = Field(
        default="1.0",
        description="Extractor version",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    metadata: Dict[str, str] = Field(default_factory=dict)


class ProvenanceCollection(BaseModel):
    """
    Collection of provenance records.
    """

    records: List[ProvenanceRecord] = Field(default_factory=list)

    def add(self, record: ProvenanceRecord) -> None:
        self.records.append(record)

    def extend(self, records: List[ProvenanceRecord]) -> None:
        self.records.extend(records)

    def by_document(self, document_id: str) -> List[ProvenanceRecord]:
        return [
            record
            for record in self.records
            if record.source_document == document_id
        ]