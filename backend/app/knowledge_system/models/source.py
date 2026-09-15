from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Source:
    """
    Represents the origin of a knowledge item.

    Every piece of knowledge should have
    provenance information.
    """

    id: str

    # Source classification
    source_type: str
    name: str

    # Location/reference
    url: Optional[str] = None
    document_id: Optional[str] = None

    # Provider information
    provider: Optional[str] = None

    # When source was created/published
    published_at: Optional[datetime] = None

    # When Orion ingested it
    ingested_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # Reliability information
    reliability_score: float = 0.0

    # Source metadata
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert source into serializable format.
        """

        return {
            "id": self.id,

            "source_type": self.source_type,
            "name": self.name,

            "url": self.url,
            "document_id": self.document_id,

            "provider": self.provider,

            "published_at": (
                self.published_at.isoformat()
                if self.published_at
                else None
            ),

            "ingested_at": (
                self.ingested_at.isoformat()
            ),

            "reliability_score": self.reliability_score,

            "metadata": self.metadata,
        }


    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> "Source":

        published_at = data.get(
            "published_at"
        )

        if isinstance(
            published_at,
            str
        ):
            published_at = datetime.fromisoformat(
                published_at
            )


        ingested_at = data.get(
            "ingested_at"
        )

        if isinstance(
            ingested_at,
            str
        ):
            ingested_at = datetime.fromisoformat(
                ingested_at
            )


        return cls(
            id=data["id"],

            source_type=data["source_type"],

            name=data["name"],

            url=data.get(
                "url"
            ),

            document_id=data.get(
                "document_id"
            ),

            provider=data.get(
                "provider"
            ),

            published_at=published_at,

            ingested_at=(
                ingested_at
                or datetime.utcnow()
            ),

            reliability_score=data.get(
                "reliability_score",
                0.0
            ),

            metadata=data.get(
                "metadata",
                {}
            ),
        )


    def is_reliable(
        self,
        threshold: float = 0.7
    ) -> bool:
        """
        Check if source passes
        reliability threshold.
        """

        return (
            self.reliability_score
            >= threshold
        )