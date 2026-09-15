"""
app/agents/risk/models.py

Canonical Pydantic models for RiskAgent.

The models represent the domain output of the RiskAgent.

They do not perform analysis or scoring.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RiskFactor(BaseModel):
    """
    Individual identified risk.
    """

    name: str

    description: str

    category: str = "business"

    severity: str = "medium"

    probability: Optional[str] = None

    impact: Optional[str] = None

    mitigation: Optional[str] = None

    evidence: List[Any] = Field(
        default_factory=list
    )


class RiskAnalysisResult(BaseModel):
    """
    Canonical output schema for RiskAgent.

    Represents a complete deterministic
    and optionally LLM-synthesized risk assessment.
    """

    company: Optional[str] = None

    overall_risk: str = "medium"

    risk_score: Optional[float] = None

    risks: List[RiskFactor] = Field(
        default_factory=list
    )

    scenarios: Any = None

    summary: str = ""

    recommendations: List[str] = Field(
        default_factory=list
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )