"""
Taxonomy enrichment.

Maps extracted entities into categories.

Example

GPT-4 -> AI Model
OpenAI -> Company
Python -> Programming Language
Redis -> Database
"""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class TaxonomyNode(BaseModel):
    """
    Single taxonomy category.
    """

    name: str

    parent: str | None = None

    description: str = ""


class EntityClassification(BaseModel):
    """
    Classification of one entity.
    """

    entity: str

    category: str

    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )


class Taxonomy(BaseModel):
    """
    Complete taxonomy.
    """

    nodes: List[TaxonomyNode] = Field(default_factory=list)

    classifications: List[EntityClassification] = Field(
        default_factory=list
    )

    def add_node(self, node: TaxonomyNode):
        self.nodes.append(node)

    def classify(self, classification: EntityClassification):
        self.classifications.append(classification)

    def get_category(self, entity: str) -> str | None:
        for c in self.classifications:
            if c.entity == entity:
                return c.category
        return None