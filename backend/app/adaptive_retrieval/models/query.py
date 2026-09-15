"""
Query Models

Represents user queries entering
the adaptive retrieval pipeline.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, List

from pydantic import BaseModel, Field


class Query(BaseModel):
    """
    User query representation.

    Contains normalized query information
    used by planner, retrievers and rankers.
    """

    id: Optional[str] = None

    text: str = Field(
        ...,
        description="Original user query"
    )

    normalized_text: Optional[str] = Field(
        default=None,
        description="Cleaned and normalized query"
    )

    language: Optional[str] = None


    # Query understanding

    intent: Optional[str] = None

    entities: List[str] = Field(
        default_factory=list
    )

    keywords: List[str] = Field(
        default_factory=list
    )


    # Metadata

    user_id: Optional[str] = None

    session_id: Optional[str] = None


    metadata: Dict[str, object] = Field(
        default_factory=dict
    )


    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )