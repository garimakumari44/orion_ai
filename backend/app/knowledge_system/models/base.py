"""
Base model shared across the Knowledge System.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """
    Common base class for all Knowledge System models.

    Provides:
    - strict validation
    - immutable-safe defaults
    - UTC timestamps
    - JSON serialization
    """

    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def touch(self) -> None:
        """
        Update the modification timestamp.
        """
        object.__setattr__(
            self,
            "updated_at",
            datetime.now(timezone.utc),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize model to a Python dictionary.
        """
        return self.model_dump()

    def to_json(self) -> str:
        """
        Serialize model to JSON.
        """
        return self.model_dump_json()