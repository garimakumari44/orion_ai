"""
app/schemas/research.py

Research API schemas.

Defines the public API contract for:

- Starting research
- Research summaries
- Research status
- Research details
- Research workspace overview
- Evidence
- Documents
- Insights
- Research reports
- Final research results

IMPORTANT ARCHITECTURAL RULE

Canonical company identity:

    company_id
    company
    ticker
    industry

Industry is distinct from sector.

The backend must never map:

    Company.sector -> industry
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Research Types
# ============================================================

ResearchType = Literal[
    "company_research",
    "company_comparison",
    "industry_research",
    "earnings_analysis",
    "valuation_analysis",
    "risk_analysis",
    "macro_research",
    "portfolio_research",
    "theme_research",
]


# ============================================================
# Research Start Request
# ============================================================


class ResearchStartRequest(BaseModel):
    """
    Request payload for starting a research project.
    """

    title: str | None = Field(
        default=None,
        description="Optional research title.",
    )

    query: str = Field(
        ...,
        min_length=3,
        description="Natural-language research question.",
    )

    company_id: int | None = Field(
        default=None,
        description="Canonical target company database ID.",
    )

    company: str | None = Field(
        default=None,
        description="Target company name.",
    )

    ticker: str | None = Field(
        default=None,
        description="Stock ticker.",
    )

    research_type: ResearchType = Field(
        default="company_research",
        description="Requested research type.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional research configuration.",
    )


# ============================================================
# Research Summary
# ============================================================


class ResearchSummary(BaseModel):
    """
    Basic information about a research project.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    title: str

    query: str

    intent: str

    research_type: ResearchType

    status: str

    company_id: int | None = None

    company: str | None = None

    ticker: str | None = None

    industry: str | None = None

    execution_plan_id: str | None = None

    created_at: datetime

    updated_at: datetime


# ============================================================
# Start Research Response
# ============================================================


class ResearchStartResponse(BaseModel):
    """
    Response returned after creating a research project.
    """

    research: ResearchSummary

    execution_plan_id: str | None = None

    message: str = (
        "Research project created successfully."
    )


# ============================================================
# Research Status
# ============================================================


class ResearchStatusResponse(BaseModel):
    """
    Live research execution status.

    Lifecycle:

        queued
            ↓
        planning
            ↓
        running
            ↓
        completed

    or:

        failed
    """

    research_id: UUID

    status: str

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    current_stage: str = "Planning"

    execution_plan_id: str | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    error: str | None = None


# ============================================================
# Research List
# ============================================================


class ResearchListResponse(BaseModel):
    """
    Response for listing research projects.
    """

    items: list[ResearchSummary] = Field(
        default_factory=list,
    )

    total: int = 0


# ============================================================
# Research Detail
# ============================================================


class ResearchDetailResponse(BaseModel):
    """
    Full research project information.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    title: str

    query: str

    intent: str

    research_type: ResearchType

    status: str

    company_id: int | None = None

    company: str | None = None

    ticker: str | None = None

    industry: str | None = None

    execution_plan_id: str | None = None

    created_at: datetime

    updated_at: datetime

    started_at: datetime | None = None

    completed_at: datetime | None = None


# ============================================================
# Research Overview
# ============================================================


class ResearchProfile(BaseModel):
    """
    Company profile displayed in the Research Workspace.
    """

    name: str | None = None

    ticker: str | None = None

    description: str | None = None

    sector: str | None = None

    industry: str | None = None

    employees: str | int | None = None

    founded: str | int | None = None


class ResearchMarket(BaseModel):
    """
    Market information displayed in the Research Workspace.

    Numeric values are accepted because research agents may
    return either formatted strings or raw numeric values.
    """

    marketCap: str | int | float | None = None

    sharePrice: str | int | float | None = None

    peRatio: str | int | float | None = None

    weekRange52: str | int | float | None = None

    dividendYield: str | int | float | None = None

    beta: str | int | float | None = None


class ResearchFinancials(BaseModel):
    """
    Financial snapshot displayed in the Research Workspace.

    Numeric values are accepted because research agents may
    return either formatted strings or raw numeric values.
    """

    revenue: str | int | float | None = None

    revenueGrowth: str | int | float | None = None

    grossMargin: str | int | float | None = None

    operatingMargin: str | int | float | None = None

    eps: str | int | float | None = None


class ResearchOverview(BaseModel):
    """
    Structured overview consumed by the frontend.
    """

    profile: ResearchProfile | None = None

    market: ResearchMarket | None = None

    financials: ResearchFinancials | None = None


# ============================================================
# Evidence
# ============================================================


class ResearchEvidence(BaseModel):
    """
    Evidence collected by research agents.
    """

    id: str | int | None = None

    title: str | None = None

    source: str | None = None

    url: str | None = None

    content: str | None = None

    excerpt: str | None = None

    date: str | None = None

    relevance: float | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# Documents
# ============================================================


class ResearchDocument(BaseModel):
    """
    Document collected during research.
    """

    id: str | int | None = None

    title: str

    type: str | None = None

    url: str | None = None

    date: str | None = None

    source: str | None = None

    description: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# Insights
# ============================================================


class ResearchInsight(BaseModel):
    """
    Structured insight generated by an agent.
    """

    id: str | int | None = None

    title: str

    summary: str | None = None

    content: str | None = None

    category: str | None = None

    confidence: float | None = None

    importance: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# Report
# ============================================================


class ResearchReportSection(BaseModel):
    """
    Individual section of the generated report.

    Content may be either:

    - plain text
    - structured dictionaries
    - lists
    - nested JSON-safe research output

    This is intentional because research agents can produce
    structured analytical sections.
    """

    id: str

    title: str

    content: Any = None

    status: Literal[
        "waiting",
        "in-progress",
        "complete",
    ] = "waiting"

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ResearchReport(BaseModel):
    """
    Final research report.
    """

    title: str | None = None

    summary: str | None = None

    sections: list[ResearchReportSection] = Field(
        default_factory=list,
    )


# ============================================================
# Research Results
# ============================================================


class ResearchResultResponse(BaseModel):
    """
    Final generated research output.

    Frontend structure:

        ResearchWorkspace
            ├── overview
            ├── evidence
            ├── documents
            ├── insights
            └── report
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    research_id: UUID

    status: str

    title: str | None = None

    company_id: int | None = None

    company: str | None = None

    ticker: str | None = None

    industry: str | None = None

    research_type: ResearchType | None = None

    # ========================================================
    # Workspace data
    # ========================================================

    overview: ResearchOverview = Field(
        default_factory=ResearchOverview,
    )

    evidence: list[ResearchEvidence] = Field(
        default_factory=list,
    )

    documents: list[ResearchDocument] = Field(
        default_factory=list,
    )

    insights: list[ResearchInsight] = Field(
        default_factory=list,
    )

    report: ResearchReport = Field(
        default_factory=ResearchReport,
    )

    # ========================================================
    # Raw execution outputs
    # ========================================================

    agent_results: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    # ========================================================
    # Backward compatibility
    # ========================================================

    citations: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    # ========================================================
    # Timestamps
    # ========================================================

    created_at: datetime | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None