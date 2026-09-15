from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlanningRequest:
    """
    Canonical planning request.

    Created by:
        PlanningParser

    Consumed by:
        Planner
        ResearchPlanner

    Represents a structured equity research request before
    task planning begins.
    """

    # =====================================================
    # ORIGINAL USER INPUT
    # =====================================================

    query: str

    # =====================================================
    # INTENT
    # =====================================================

    # Example:
    # company_research
    # company_comparison
    # industry_research
    # valuation_analysis
    # earnings_analysis
    intent: str = "general"

    # Higher-level research category
    # company
    # industry
    # comparison
    # valuation
    # earnings
    # macro
    # portfolio
    # theme
    research_type: str = "general"

    # =====================================================
    # RESEARCH TARGETS
    # =====================================================

    companies: List[str] = field(default_factory=list)

    tickers: List[str] = field(default_factory=list)

    industries: List[str] = field(default_factory=list)

    sectors: List[str] = field(default_factory=list)

    comparison_targets: List[str] = field(default_factory=list)

    themes: List[str] = field(default_factory=list)

    # =====================================================
    # PARSED INFORMATION
    # =====================================================

    entities: List[str] = field(default_factory=list)

    constraints: List[str] = field(default_factory=list)

    # latest
    # quarterly
    # annual
    # historical
    time_horizon: Optional[str] = None

    # =====================================================
    # PLANNING FLAGS
    # =====================================================

    requires_retrieval: bool = True

    required_tools: List[str] = field(default_factory=list)

    priority: str = "normal"

    # =====================================================
    # CONTEXT
    # =====================================================

    context: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    # =====================================================
    # SESSION
    # =====================================================

    user_id: Optional[str] = None

    session_id: Optional[str] = None