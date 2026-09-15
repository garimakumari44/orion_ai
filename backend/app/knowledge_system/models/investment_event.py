from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class InvestmentEvent:
    """
    Represents an investment-relevant event.

    Examples:
    - Earnings release
    - CEO change
    - Product launch
    - Acquisition
    - Regulatory action
    - Interest rate decision
    - Guidance revision
    - Market event
    """

    id: str

    # Event classification
    event_type: str
    title: str

    # When event happened
    timestamp: datetime

    # Entities involved
    company_ids: List[str] = field(default_factory=list)
    entity_ids: List[str] = field(default_factory=list)

    # Event description
    description: Optional[str] = None

    # Impact analysis
    sentiment: Optional[str] = None
    impact_level: Optional[str] = None

    # Investment relevance
    affected_sectors: List[str] = field(default_factory=list)
    affected_assets: List[str] = field(default_factory=list)

    # Financial impact
    financial_metrics: Dict[str, Any] = field(default_factory=dict)

    # Source information
    source: Optional[str] = None
    source_url: Optional[str] = None

    # Confidence from extraction model
    confidence: float = 0.0

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event into serializable dictionary.
        """

        return {
            "id": self.id,
            "event_type": self.event_type,
            "title": self.title,
            "timestamp": self.timestamp.isoformat(),

            "company_ids": self.company_ids,
            "entity_ids": self.entity_ids,

            "description": self.description,

            "sentiment": self.sentiment,
            "impact_level": self.impact_level,

            "affected_sectors": self.affected_sectors,
            "affected_assets": self.affected_assets,

            "financial_metrics": self.financial_metrics,

            "source": self.source,
            "source_url": self.source_url,

            "confidence": self.confidence,

            "metadata": self.metadata,
        }


    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> "InvestmentEvent":

        timestamp = data.get("timestamp")

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            id=data["id"],
            event_type=data["event_type"],
            title=data["title"],
            timestamp=timestamp,

            company_ids=data.get(
                "company_ids",
                []
            ),

            entity_ids=data.get(
                "entity_ids",
                []
            ),

            description=data.get(
                "description"
            ),

            sentiment=data.get(
                "sentiment"
            ),

            impact_level=data.get(
                "impact_level"
            ),

            affected_sectors=data.get(
                "affected_sectors",
                []
            ),

            affected_assets=data.get(
                "affected_assets",
                []
            ),

            financial_metrics=data.get(
                "financial_metrics",
                {}
            ),

            source=data.get(
                "source"
            ),

            source_url=data.get(
                "source_url"
            ),

            confidence=data.get(
                "confidence",
                0.0
            ),

            metadata=data.get(
                "metadata",
                {}
            ),
        )


    def is_high_impact(self) -> bool:
        """
        Determines whether this event
        can affect investment decisions.
        """

        return self.impact_level in {
            "high",
            "critical"
        }


    def add_company(self, company_id: str):
        """
        Attach company entity.
        """

        if company_id not in self.company_ids:
            self.company_ids.append(company_id)


    def add_relation_entity(self, entity_id: str):
        """
        Attach related knowledge entities.
        """

        if entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)