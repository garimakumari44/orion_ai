"""
User preference models.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PreferenceType(str, Enum):
    """Supported preference categories."""

    LANGUAGE = "language"
    FORMAT = "format"
    REPORT = "report"
    WRITING = "writing"
    CODING = "coding"
    RESEARCH = "research"
    UI = "ui"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


class PreferenceScope(str, Enum):
    """Preference scope."""

    GLOBAL = "global"
    WORKSPACE = "workspace"
    PROJECT = "project"
    SESSION = "session"


class Preference(BaseModel):
    """
    Represents a single user preference.
    """

    id: str

    user_id: str

    key: str

    value: Any

    type: PreferenceType = PreferenceType.CUSTOM

    scope: PreferenceScope = PreferenceScope.GLOBAL

    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    source: str = "user"

    description: str | None = None

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    active: bool = True