from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Resource(BaseModel):
    """
    Represents a resource exposed by an MCP server.

    A resource is read-only context/data that an MCP client
    can discover and retrieve.
    """

    id: str = Field(
        ...,
        description="Unique identifier of the resource"
    )

    uri: str = Field(
        ...,
        description="URI used to access the resource"
    )

    name: str = Field(
        ...,
        description="Human-readable resource name"
    )

    description: Optional[str] = Field(
        default=None,
        description="Description of what the resource contains"
    )

    mime_type: Optional[str] = Field(
        default=None,
        alias="mimeType",
        description="Content type of the resource"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional resource metadata"
    )

    readable: bool = Field(
        default=True,
        description="Whether this resource can be read"
    )

    created_at: Optional[str] = Field(
        default=None,
        description="Resource creation timestamp"
    )

    updated_at: Optional[str] = Field(
        default=None,
        description="Last update timestamp"
    )

    model_config = {
        "populate_by_name": True
    }