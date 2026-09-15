from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    REFERENCES = "references"
    CITES = "cites"
    RELATED_TO = "related_to"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    PART_OF = "part_of"
    DUPLICATE_OF = "duplicate_of"
    SIMILAR_TO = "similar_to"
    DEPENDS_ON = "depends_on"
    AUTHORED_BY = "authored_by"
    LOCATED_IN = "located_in"


class Relationship(BaseModel):
    """
    Graph edge connecting two entities/documents/chunks.
    """

    id: UUID = Field(default_factory=uuid4)

    source_id: UUID
    target_id: UUID

    relationship: RelationshipType

    confidence: float = 1.0

    weight: float = 1.0

    description: Optional[str] = None

    metadata: Dict[str, str] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)