"""
Metadata models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field

from .base import BaseModel


class Metadata(BaseModel):
    """
    Metadata attached to a document.
    """

    id: UUID = Field(default_factory=uuid4)

    document_id: UUID

    author: Optional[str] = None

    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None

    mime_type: Optional[str] = None
    encoding: Optional[str] = None

    language: Optional[str] = None

    keywords: List[str] = Field(default_factory=list)

    custom_fields: Dict[str, Any] = Field(default_factory=dict)