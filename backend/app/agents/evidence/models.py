"""
Evidence Agent Models

Data structures for evidence,
citations, and source tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any



@dataclass
class EvidenceItem:
    """
    Represents one evidence record.
    """

    claim: str

    source: str

    document: str = ""

    date: str = ""

    confidence: float = 0.0

    verified: bool = False



@dataclass
class Citation:
    """
    Research citation object.
    """

    claim: str

    source: str

    url: str = ""

    page: str = ""

    confidence: float = 0.0



@dataclass
class SourceRecord:
    """
    Stores source information.
    """

    name: str

    source_type: str

    reliability_score: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )



@dataclass
class EvidenceReport:
    """
    Complete evidence analysis output.
    """

    research_id: str = ""

    evidence_count: int = 0

    citations: List[Citation] = field(
        default_factory=list
    )

    conflicts: List[str] = field(
        default_factory=list
    )

    confidence_score: float = 0.0

    status: str = "completed"