"""
Knowledge graph models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from pydantic import Field

from .base import BaseModel


class GraphNode(BaseModel):
    """
    Node within the knowledge graph.
    """

    id: UUID = Field(default_factory=uuid4)

    label: str
    node_type: str

    properties: Dict[str, Any] = Field(default_factory=dict)

    document_id: Optional[UUID] = None
    entity_id: Optional[UUID] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class GraphEdge(BaseModel):
    """
    Edge connecting two graph nodes.
    """

    id: UUID = Field(default_factory=uuid4)

    source_node: UUID
    target_node: UUID

    relation: str

    weight: float = 1.0
    confidence: float = 1.0

    properties: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeGraph(BaseModel):
    """
    Complete graph representation.
    """

    id: UUID = Field(default_factory=uuid4)

    name: str

    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)