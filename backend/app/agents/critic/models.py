"""
Critic Agent Data Models

Defines structures used for:
- Verification results
- Hallucination reports
- Quality scoring
- Citation analysis
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any



@dataclass
class ClaimEvaluation:
    """
    Represents evaluation of a single claim.
    """

    claim: str

    confidence: float = 0.0

    status: str = "pending"

    evidence: List[str] = field(
        default_factory=list
    )

    issues: List[str] = field(
        default_factory=list
    )



@dataclass
class VerificationResult:
    """
    Stores verification output.
    """

    total_claims: int = 0

    verified_claims: int = 0

    failed_claims: int = 0

    confidence_score: float = 0.0

    claims: List[ClaimEvaluation] = field(
        default_factory=list
    )



@dataclass
class HallucinationReport:
    """
    Stores hallucination analysis.
    """

    risk_level: str = "low"

    risk_score: float = 0.0

    detected_issues: List[str] = field(
        default_factory=list
    )

    suspicious_claims: List[str] = field(
        default_factory=list
    )



@dataclass
class CitationAnalysis:
    """
    Citation quality analysis.
    """

    total_claims: int = 0

    supported_claims: int = 0

    missing_citations: int = 0

    citation_score: float = 0.0

    sources: List[str] = field(
        default_factory=list
    )



@dataclass
class ResearchQualityScore:
    """
    Overall research quality score.
    """

    final_score: float = 0.0

    rating: str = "unknown"

    accuracy: float = 0.0

    evidence_quality: float = 0.0

    reasoning_quality: float = 0.0

    citation_quality: float = 0.0

    completeness: float = 0.0



@dataclass
class CriticReport:
    """
    Complete critic output.

    Used by:
    - Investment Committee Agent
    - Report Generator
    - Dashboard Analytics
    """

    agent_name: str = "critic_agent"

    research_id: str = ""

    verification: Dict[str, Any] = field(
        default_factory=dict
    )

    hallucination: Dict[str, Any] = field(
        default_factory=dict
    )

    citations: Dict[str, Any] = field(
        default_factory=dict
    )

    quality_score: Dict[str, Any] = field(
        default_factory=dict
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    status: str = "completed"