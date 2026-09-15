from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ServerMetadata(BaseModel):
    """
    Metadata describing an MCP server.

    Used during discovery and registration.
    """

    name: str = Field(
        ...,
        description="Unique name of the MCP server"
    )

    description: Optional[str] = Field(
        default=None,
        description="Human readable description"
    )

    version: str = Field(
        default="1.0.0",
        description="Server version"
    )

    provider: Optional[str] = Field(
        default=None,
        description="Organization or developer providing the server"
    )

    capabilities: List[str] = Field(
        default_factory=list,
        description="Capabilities supported by this server"
    )

    tools: List[str] = Field(
        default_factory=list,
        description="Tools exposed by this server"
    )

    resources: List[str] = Field(
        default_factory=list,
        description="Resources exposed by this server"
    )

    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional custom metadata"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )


    def update_timestamp(self):
        """
        Update modification time.
        """

        self.updated_at = datetime.utcnow()