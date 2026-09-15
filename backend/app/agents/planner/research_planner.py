"""
app/agents/planner/research_planner.py

Research Planner

Responsible for converting a research request into an executable
set of research tasks.

The ResearchPlanner DOES NOT execute agents.

It decides:

    research_type
        ↓
    required research tasks
        ↓
    capability
        ↓
    agent_name
        ↓
    dependencies

Execution is handled later by:

    ExecutionPlanBuilder
        ↓
    ExecutionEngine
        ↓
    Worker
        ↓
    AgentManager
        ↓
    Registered Agent

Supported Research Types:

1. company_research
2. industry_research
3. company_comparison
4. theme_research
5. portfolio_research
6. macro_research
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from app.planning.models.task import (
    Task,
    TaskPriority,
    TaskType,
)


class ResearchPlanner:
    """
    Creates executable research tasks for equity research workflows.

    The planner is deterministic.

    It does not:
        - execute agents
        - call the LLM
        - retrieve documents
        - access databases
        - perform research
        - construct the final report

    It only determines:

        WHAT needs to be researched
        WHO should research it
        IN WHAT ORDER it should execute
    """

    # ============================================================
    # Research Types
    # ============================================================

    COMPANY_RESEARCH = "company_research"
    INDUSTRY_RESEARCH = "industry_research"
    COMPANY_COMPARISON = "company_comparison"
    THEME_RESEARCH = "theme_research"
    PORTFOLIO_RESEARCH = "portfolio_research"
    MACRO_RESEARCH = "macro_research"

    # ============================================================
    # Agent IDs
    # ============================================================

    COMPANY_AGENT = "company"
    FINANCIAL_AGENT = "financial"
    INDUSTRY_AGENT = "industry"
    VALUATION_AGENT = "valuation"
    RISK_AGENT = "risk"
    COMPARISON_AGENT = "comparison"
    THEME_AGENT = "theme"
    PORTFOLIO_AGENT = "portfolio"
    MACRO_AGENT = "macro"

    EVIDENCE_AGENT = "evidence"
    CRITIC_AGENT = "critic"
    INVESTMENT_COMMITTEE = "investment_committee"

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self) -> None:
        """
        Initialize the research planner.

        The planner is intentionally stateless.
        """
        pass

    # ============================================================
    # Public API
    # ============================================================

    def plan(
        self,
        research_type: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Task]:
        """
        Create research tasks for the requested research type.
        """

        parameters = dict(parameters or {})

        normalized_type = self._normalize_research_type(
            research_type
        )

        if normalized_type == self.COMPANY_RESEARCH:
            return self._plan_company_research(parameters)

        if normalized_type == self.INDUSTRY_RESEARCH:
            return self._plan_industry_research(parameters)

        if normalized_type == self.COMPANY_COMPARISON:
            return self._plan_company_comparison(parameters)

        if normalized_type == self.THEME_RESEARCH:
            return self._plan_theme_research(parameters)

        if normalized_type == self.PORTFOLIO_RESEARCH:
            return self._plan_portfolio_research(parameters)

        if normalized_type == self.MACRO_RESEARCH:
            return self._plan_macro_research(parameters)

        raise ValueError(
            f"Unsupported research type: {research_type}"
        )

    # ============================================================
    # Normalization
    # ============================================================

    def _normalize_research_type(
        self,
        research_type: str,
    ) -> str:
        """
        Normalize research type values coming from the API/frontend.
        """

        if not research_type:
            raise ValueError(
                "research_type is required"
            )

        value = research_type.strip().lower()

        aliases = {
            "company": self.COMPANY_RESEARCH,
            "company_research": self.COMPANY_RESEARCH,
            "company-analysis": self.COMPANY_RESEARCH,
            "company_analysis": self.COMPANY_RESEARCH,

            "industry": self.INDUSTRY_RESEARCH,
            "industry_research": self.INDUSTRY_RESEARCH,
            "sector": self.INDUSTRY_RESEARCH,
            "sector_research": self.INDUSTRY_RESEARCH,

            "comparison": self.COMPANY_COMPARISON,
            "company_comparison": self.COMPANY_COMPARISON,
            "company-comparison": self.COMPANY_COMPARISON,

            "theme": self.THEME_RESEARCH,
            "theme_research": self.THEME_RESEARCH,
            "investment_theme": self.THEME_RESEARCH,

            "portfolio": self.PORTFOLIO_RESEARCH,
            "portfolio_research": self.PORTFOLIO_RESEARCH,

            "macro": self.MACRO_RESEARCH,
            "macro_research": self.MACRO_RESEARCH,
            "market_macro": self.MACRO_RESEARCH,
        }

        normalized = aliases.get(value)

        if normalized is None:
            raise ValueError(
                f"Unsupported research type: {research_type}. "
                f"Supported types: "
                f"{self.COMPANY_RESEARCH}, "
                f"{self.INDUSTRY_RESEARCH}, "
                f"{self.COMPANY_COMPARISON}, "
                f"{self.THEME_RESEARCH}, "
                f"{self.PORTFOLIO_RESEARCH}, "
                f"{self.MACRO_RESEARCH}"
            )

        return normalized

    # ============================================================
    # Task Factory
    # ============================================================

    def _create_task(
        self,
        *,
        title: str,
        description: str,
        task_type: TaskType,
        capability: str,
        agent_name: str,
        parameters: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        parallelizable: bool = True,
        failure_policy: str = "retry",
        cost: str = "low",
        planner_reasoning: Optional[str] = None,
    ) -> Task:
        """
        Create a canonical Task.

        The planner is responsible for deciding which registered
        agent should execute the task.

        ExecutionPlanBuilder and the execution layer must not
        replace this assignment.
        """

        return Task(
            id=f"research-{uuid.uuid4().hex}",
            title=title,
            description=description,
            task_type=task_type,
            capability=capability,
            priority=priority,
            dependencies=list(dependencies or []),
            parallelizable=parallelizable,
            parameters=dict(parameters),
            agent_name=agent_name,
            cost=cost,
            planner_reasoning=planner_reasoning,
        )

    # ============================================================
    # Parameter Helpers
    # ============================================================

    def _research_parameters(
        self,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Preserve the complete research request.

        The planner should not throw away parameters supplied by
        ResearchService/API.
        """

        return dict(parameters)

    # ============================================================
    # Company Research
    # ============================================================

    def _plan_company_research(
        self,
        parameters: Dict[str, Any],
    ) -> List[Task]:
        """
        Create a company research workflow.

        Dependency graph:

            Company Research ─────┐
                                  │
            Financial Research ───┼──> Valuation ───┐
                                  │                 │
            Industry Research ────┼──> Risk ────────┤
                                  │                 │
                                  └──> Evidence ─────┤
                                                    ↓
                                                  Critic
                                                    ↓
                                             Investment Thesis
                                                    ↓
                                                Final Report
        """

        params = self._research_parameters(parameters)

        company = self._create_task(
            title="Company Research",
            description=(
                "Research the target company's business, products, "
                "competitive position, management, and strategic profile."
            ),
            task_type=TaskType.COMPANY_LOOKUP,
            capability="company_research",
            agent_name=self.COMPANY_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Establish the fundamental company profile "
                "before downstream analysis."
            ),
        )

        financial = self._create_task(
            title="Financial Analysis",
            description=(
                "Analyze financial statements, fundamentals, growth, "
                "profitability, cash flow, and financial trends."
            ),
            task_type=TaskType.FINANCIAL_DATA,
            capability="financial_analysis",
            agent_name=self.FINANCIAL_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Financial data is required for valuation "
                "and investment analysis."
            ),
        )

        industry = self._create_task(
            title="Industry Analysis",
            description=(
                "Analyze the company's industry, sector dynamics, "
                "competitors, market structure, and growth drivers."
            ),
            task_type=TaskType.ANALYZE,
            capability="industry_analysis",
            agent_name=self.INDUSTRY_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Industry context is required to evaluate "
                "competitive position and market opportunity."
            ),
        )

        valuation = self._create_task(
            title="Valuation Analysis",
            description=(
                "Evaluate valuation using available financial "
                "and market information."
            ),
            task_type=TaskType.REASON,
            capability="valuation_analysis",
            agent_name=self.VALUATION_AGENT,
            parameters=params,
            dependencies=[
                company.id,
                financial.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Valuation depends on company and financial research."
            ),
        )

        risk = self._create_task(
            title="Risk Analysis",
            description=(
                "Identify company, industry, financial, regulatory, "
                "competitive, and market risks."
            ),
            task_type=TaskType.ANALYZE,
            capability="risk_analysis",
            agent_name=self.RISK_AGENT,
            parameters=params,
            dependencies=[
                company.id,
                financial.id,
                industry.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Risk analysis requires company, financial, "
                "and industry context."
            ),
        )

        evidence = self._create_task(
            title="Evidence Validation",
            description=(
                "Validate important claims and identify supporting "
                "evidence and data quality issues."
            ),
            task_type=TaskType.VALIDATE,
            capability="evidence_validation",
            agent_name=self.EVIDENCE_AGENT,
            parameters=params,
            dependencies=[
                company.id,
                financial.id,
                industry.id,
                valuation.id,
                risk.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Evidence validation should occur after the "
                "primary research analyses are available."
            ),
        )

        critic = self._create_task(
            title="Research Critique",
            description=(
                "Critically review the research for contradictions, "
                "unsupported claims, missing evidence, and analytical weaknesses."
            ),
            task_type=TaskType.VALIDATE,
            capability="research_critique",
            agent_name=self.CRITIC_AGENT,
            parameters=params,
            dependencies=[
                company.id,
                financial.id,
                industry.id,
                valuation.id,
                risk.id,
                evidence.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Critique requires the complete research evidence base."
            ),
        )

        thesis = self._create_task(
            title="Investment Thesis",
            description=(
                "Synthesize research into an investment thesis including "
                "opportunity, catalysts, risks, and key assumptions."
            ),
            task_type=TaskType.REASON,
            capability="investment_thesis",
            agent_name=self.INVESTMENT_COMMITTEE,
            parameters=params,
            dependencies=[
                company.id,
                financial.id,
                industry.id,
                valuation.id,
                risk.id,
                evidence.id,
                critic.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "The investment thesis is the final analytical "
                "synthesis of the validated research."
            ),
        )

        report = self._create_task(
            title="Generate Research Report",
            description=(
                "Generate the final structured equity research report "
                "from the completed research workflow."
            ),
            task_type=TaskType.GENERATE_REPORT,
            capability="research_report_generation",
            agent_name=self.INVESTMENT_COMMITTEE,
            parameters=params,
            dependencies=[
                thesis.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "The final report must be generated only after "
                "the investment thesis is complete."
            ),
        )

        return [
            company,
            financial,
            industry,
            valuation,
            risk,
            evidence,
            critic,
            thesis,
            report,
        ]

    # ============================================================
    # Industry Research
    # ============================================================

    def _plan_industry_research(
        self,
        parameters: Dict[str, Any],
    ) -> List[Task]:
        """
        Create an industry research workflow.

        Dependency graph:

            Industry Research ──┐
            Market Research ───┼──> Competitive Analysis
            Macro Research ────┘             │
                                             ↓
                                           Risks
                                             ↓
                                          Evidence
                                             ↓
                                           Critic
                                             ↓
                                      Final Research
        """

        params = self._research_parameters(parameters)

        industry = self._create_task(
            title="Industry Research",
            description=(
                "Research industry structure, size, growth, "
                "segmentation, and major participants."
            ),
            task_type=TaskType.ANALYZE,
            capability="industry_research",
            agent_name=self.INDUSTRY_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Establish the core industry landscape."
            ),
        )

        market = self._create_task(
            title="Market Research",
            description=(
                "Analyze market size, growth drivers, trends, demand, "
                "and addressable opportunities."
            ),
            task_type=TaskType.SEARCH,
            capability="market_research",
            agent_name=self.INDUSTRY_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Market dynamics are required to understand "
                "industry opportunity."
            ),
        )

        macro = self._create_task(
            title="Macro Research",
            description=(
                "Analyze macroeconomic factors affecting "
                "the target industry."
            ),
            task_type=TaskType.ANALYZE,
            capability="macro_analysis",
            agent_name=self.MACRO_AGENT,
            parameters=params,
            priority=TaskPriority.MEDIUM,
            planner_reasoning=(
                "Macro conditions can materially affect "
                "industry growth and risk."
            ),
        )

        competitive = self._create_task(
            title="Competitive Landscape",
            description=(
                "Analyze major competitors, market shares, "
                "competitive advantages, and industry structure."
            ),
            task_type=TaskType.COMPARE,
            capability="competitive_analysis",
            agent_name=self.COMPARISON_AGENT,
            parameters=params,
            dependencies=[
                industry.id,
                market.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Competitive analysis requires the industry "
                "and market context."
            ),
        )

        risk = self._create_task(
            title="Industry Risk Analysis",
            description=(
                "Identify structural, regulatory, technological, "
                "competitive, and macro risks."
            ),
            task_type=TaskType.ANALYZE,
            capability="industry_risk_analysis",
            agent_name=self.RISK_AGENT,
            parameters=params,
            dependencies=[
                industry.id,
                market.id,
                macro.id,
                competitive.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Industry risks require the complete industry landscape."
            ),
        )

        evidence = self._create_task(
            title="Industry Evidence Validation",
            description=(
                "Validate important industry claims "
                "and supporting evidence."
            ),
            task_type=TaskType.VALIDATE,
            capability="evidence_validation",
            agent_name=self.EVIDENCE_AGENT,
            parameters=params,
            dependencies=[
                industry.id,
                market.id,
                macro.id,
                competitive.id,
                risk.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Validate the complete industry research before synthesis."
            ),
        )

        critic = self._create_task(
            title="Industry Research Critique",
            description=(
                "Critically review the industry research for "
                "unsupported assumptions and analytical gaps."
            ),
            task_type=TaskType.VALIDATE,
            capability="research_critique",
            agent_name=self.CRITIC_AGENT,
            parameters=params,
            dependencies=[
                evidence.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Critique should operate on validated research."
            ),
        )

        report = self._create_task(
            title="Generate Industry Research Report",
            description=(
                "Generate the final industry research report."
            ),
            task_type=TaskType.GENERATE_REPORT,
            capability="research_report_generation",
            agent_name=self.INVESTMENT_COMMITTEE,
            parameters=params,
            dependencies=[
                critic.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "Generate the report after research validation and critique."
            ),
        )

        return [
            industry,
            market,
            macro,
            competitive,
            risk,
            evidence,
            critic,
            report,
        ]

    # ============================================================
    # Company Comparison
    # ============================================================

    def _plan_company_comparison(
        self,
        parameters: Dict[str, Any],
    ) -> List[Task]:
        """
        Create a multi-company comparison workflow.
        """

        params = self._research_parameters(parameters)

        company_data = self._create_task(
            title="Collect Company Data",
            description=(
                "Collect comparable company profiles "
                "and fundamental data."
            ),
            task_type=TaskType.COMPANY_LOOKUP,
            capability="company_research",
            agent_name=self.COMPANY_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Collect standardized company information "
                "before comparison."
            ),
        )

        financials = self._create_task(
            title="Collect Financial Data",
            description=(
                "Collect standardized financial and fundamental "
                "metrics for all companies."
            ),
            task_type=TaskType.FINANCIAL_DATA,
            capability="financial_analysis",
            agent_name=self.FINANCIAL_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Financial normalization is required "
                "for meaningful company comparison."
            ),
        )

        industry = self._create_task(
            title="Analyze Competitive Context",
            description=(
                "Analyze the industry and competitive position "
                "of the companies being compared."
            ),
            task_type=TaskType.ANALYZE,
            capability="industry_analysis",
            agent_name=self.INDUSTRY_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Comparison requires a shared industry context."
            ),
        )

        comparison = self._create_task(
            title="Compare Companies",
            description=(
                "Compare companies across financials, growth, "
                "profitability, valuation, competitive position, and risks."
            ),
            task_type=TaskType.COMPARE,
            capability="company_comparison",
            agent_name=self.COMPARISON_AGENT,
            parameters=params,
            dependencies=[
                company_data.id,
                financials.id,
                industry.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "Comparison depends on standardized company, "
                "financial, and industry information."
            ),
        )

        valuation = self._create_task(
            title="Compare Valuations",
            description=(
                "Compare relative valuations and valuation "
                "multiples across the companies."
            ),
            task_type=TaskType.REASON,
            capability="valuation_analysis",
            agent_name=self.VALUATION_AGENT,
            parameters=params,
            dependencies=[
                financials.id,
                comparison.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Relative valuation requires normalized financial "
                "and comparison data."
            ),
        )

        risk = self._create_task(
            title="Compare Risks",
            description=(
                "Compare the key risks and vulnerabilities "
                "of the companies."
            ),
            task_type=TaskType.ANALYZE,
            capability="risk_analysis",
            agent_name=self.RISK_AGENT,
            parameters=params,
            dependencies=[
                company_data.id,
                industry.id,
                comparison.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Risk comparison requires company "
                "and competitive context."
            ),
        )

        evidence = self._create_task(
            title="Validate Comparison Evidence",
            description=(
                "Validate the evidence supporting "
                "the comparative conclusions."
            ),
            task_type=TaskType.VALIDATE,
            capability="evidence_validation",
            agent_name=self.EVIDENCE_AGENT,
            parameters=params,
            dependencies=[
                comparison.id,
                valuation.id,
                risk.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Validate comparative claims before synthesis."
            ),
        )

        critic = self._create_task(
            title="Critique Company Comparison",
            description=(
                "Review the comparison for bias, missing metrics, "
                "unsupported conclusions, and inconsistencies."
            ),
            task_type=TaskType.VALIDATE,
            capability="research_critique",
            agent_name=self.CRITIC_AGENT,
            parameters=params,
            dependencies=[
                evidence.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Critique the validated comparison "
                "before producing conclusions."
            ),
        )

        report = self._create_task(
            title="Generate Comparison Report",
            description=(
                "Generate the final company comparison report."
            ),
            task_type=TaskType.GENERATE_REPORT,
            capability="research_report_generation",
            agent_name=self.INVESTMENT_COMMITTEE,
            parameters=params,
            dependencies=[
                critic.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "The report should be generated "
                "from the validated comparison."
            ),
        )

        return [
            company_data,
            financials,
            industry,
            comparison,
            valuation,
            risk,
            evidence,
            critic,
            report,
        ]

    # ============================================================
    # Theme Research
    # ============================================================

    def _plan_theme_research(
        self,
        parameters: Dict[str, Any],
    ) -> List[Task]:
        """
        Create an investment-theme research workflow.
        """

        params = self._research_parameters(parameters)

        theme = self._create_task(
            title="Theme Research",
            description=(
                "Research the investment theme, definition, scope, "
                "trends, and structural drivers."
            ),
            task_type=TaskType.SEARCH,
            capability="theme_research",
            agent_name=self.THEME_AGENT,
            parameters=params,
            priority=TaskPriority.HIGH,
            planner_reasoning=(
                "Establish the investment theme "
                "and its structural drivers."
            ),
        )

        industry = self._create_task(
            title="Theme Industry Analysis",
            description=(
                "Identify industries and sectors exposed "
                "to the investment theme."
            ),
            task_type=TaskType.ANALYZE,
            capability="industry_analysis",
            agent_name=self.INDUSTRY_AGENT,
            parameters=params,
            dependencies=[
                theme.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Industry exposure depends on understanding the theme."
            ),
        )

        companies = self._create_task(
            title="Identify Theme Companies",
            description=(
                "Identify companies with meaningful exposure "
                "to the investment theme."
            ),
            task_type=TaskType.COMPANY_LOOKUP,
            capability="company_research",
            agent_name=self.COMPANY_AGENT,
            parameters=params,
            dependencies=[
                theme.id,
                industry.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Company identification requires both theme "
                "and industry context."
            ),
        )

        comparison = self._create_task(
            title="Compare Theme Opportunities",
            description=(
                "Compare companies and opportunities "
                "exposed to the theme."
            ),
            task_type=TaskType.COMPARE,
            capability="company_comparison",
            agent_name=self.COMPARISON_AGENT,
            parameters=params,
            dependencies=[
                companies.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Compare the identified theme beneficiaries."
            ),
        )

        risks = self._create_task(
            title="Theme Risk Analysis",
            description=(
                "Analyze structural, regulatory, technological, "
                "market, and adoption risks."
            ),
            task_type=TaskType.ANALYZE,
            capability="risk_analysis",
            agent_name=self.RISK_AGENT,
            parameters=params,
            dependencies=[
                theme.id,
                industry.id,
                comparison.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Theme risks require the complete theme "
                "and opportunity analysis."
            ),
        )

        evidence = self._create_task(
            title="Validate Theme Evidence",
            description=(
                "Validate claims and evidence supporting "
                "the theme analysis."
            ),
            task_type=TaskType.VALIDATE,
            capability="evidence_validation",
            agent_name=self.EVIDENCE_AGENT,
            parameters=params,
            dependencies=[
                theme.id,
                industry.id,
                companies.id,
                comparison.id,
                risks.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Validate the complete theme research before synthesis."
            ),
        )

        critic = self._create_task(
            title="Critique Theme Research",
            description=(
                "Critically review theme assumptions, evidence, "
                "opportunity selection, and risks."
            ),
            task_type=TaskType.VALIDATE,
            capability="research_critique",
            agent_name=self.CRITIC_AGENT,
            parameters=params,
            dependencies=[
                evidence.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Critique the validated theme research."
            ),
        )

        report = self._create_task(
            title="Generate Theme Research Report",
            description=(
                "Generate the final investment theme research report."
            ),
            task_type=TaskType.GENERATE_REPORT,
            capability="research_report_generation",
            agent_name=self.INVESTMENT_COMMITTEE,
            parameters=params,
            dependencies=[
                critic.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "Produce the final report after "
                "validation and critique."
            ),
        )

        return [
            theme,
            industry,
            companies,
            comparison,
            risks,
            evidence,
            critic,
            report,
        ]

    # ============================================================
    # Portfolio Research
    # ============================================================

    def _plan_portfolio_research(
        self,
        parameters: Dict[str, Any],
    ) -> List[Task]:
        """
        Create a portfolio research workflow.
        """

        params = self._research_parameters(parameters)

        portfolio = self._create_task(
            title="Analyze Portfolio",
            description=(
                "Analyze portfolio holdings, weights, exposures, "
                "concentration, and performance."
            ),
            task_type=TaskType.ANALYZE,
            capability="portfolio_analysis",
            agent_name=self.PORTFOLIO_AGENT,
            parameters=params,
            priority=TaskPriority.CRITICAL,
            planner_reasoning=(
                "Establish the current portfolio structure."
            ),
        )

        companies = self._create_task(
            title="Research Portfolio Companies",
            description=(
                "Research the fundamental position of companies "
                "held in the portfolio."
            ),
            task_type=TaskType.COMPANY_LOOKUP,
            capability="company_research",
            agent_name=self.COMPANY_AGENT,
            parameters=params,
            dependencies=[
                portfolio.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Company research should use the portfolio "
                "holdings as its scope."
            ),
        )

        financials = self._create_task(
            title="Analyze Portfolio Financials",
            description=(
                "Analyze financial fundamentals and valuation "
                "metrics for portfolio holdings."
            ),
            task_type=TaskType.FINANCIAL_DATA,
            capability="financial_analysis",
            agent_name=self.FINANCIAL_AGENT,
            parameters=params,
            dependencies=[
                portfolio.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Financial analysis should cover "
                "the identified portfolio holdings."
            ),
        )

        risks = self._create_task(
            title="Analyze Portfolio Risks",
            description=(
                "Analyze concentration, company, sector, "
                "macroeconomic, and portfolio-level risks."
            ),
            task_type=TaskType.ANALYZE,
            capability="portfolio_risk_analysis",
            agent_name=self.RISK_AGENT,
            parameters=params,
            dependencies=[
                portfolio.id,
                companies.id,
                financials.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "Portfolio risk requires portfolio structure "
                "and holding-level research."
            ),
        )

        valuation = self._create_task(
            title="Analyze Portfolio Valuation",
            description=(
                "Evaluate valuation and relative attractiveness "
                "of portfolio holdings."
            ),
            task_type=TaskType.REASON,
            capability="valuation_analysis",
            agent_name=self.VALUATION_AGENT,
            parameters=params,
            dependencies=[
                companies.id,
                financials.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Portfolio valuation requires company "
                "and financial analysis."
            ),
        )

        evidence = self._create_task(
            title="Validate Portfolio Evidence",
            description=(
                "Validate portfolio-level analytical claims "
                "and supporting evidence."
            ),
            task_type=TaskType.VALIDATE,
            capability="evidence_validation",
            agent_name=self.EVIDENCE_AGENT,
            parameters=params,
            dependencies=[
                portfolio.id,
                companies.id,
                financials.id,
                risks.id,
                valuation.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Validate all major portfolio conclusions."
            ),
        )

        critic = self._create_task(
            title="Critique Portfolio Analysis",
            description=(
                "Critically review portfolio recommendations, "
                "assumptions, concentration, and risks."
            ),
            task_type=TaskType.VALIDATE,
            capability="research_critique",
            agent_name=self.CRITIC_AGENT,
            parameters=params,
            dependencies=[
                evidence.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Critique the validated portfolio analysis."
            ),
        )

        report = self._create_task(
            title="Generate Portfolio Research Report",
            description=(
                "Generate the final portfolio research "
                "and recommendation report."
            ),
            task_type=TaskType.GENERATE_REPORT,
            capability="research_report_generation",
            agent_name=self.INVESTMENT_COMMITTEE,
            parameters=params,
            dependencies=[
                critic.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "Generate the final portfolio report "
                "after validation and critique."
            ),
        )

        return [
            portfolio,
            companies,
            financials,
            risks,
            valuation,
            evidence,
            critic,
            report,
        ]

    # ============================================================
    # Macro Research
    # ============================================================

    def _plan_macro_research(
        self,
        parameters: Dict[str, Any],
    ) -> List[Task]:
        """
        Create a macroeconomic research workflow.
        """

        params = self._research_parameters(parameters)

        macro = self._create_task(
            title="Macro Economic Research",
            description=(
                "Research economic growth, inflation, interest rates, "
                "monetary policy, fiscal policy, and major macro trends."
            ),
            task_type=TaskType.MARKET_DATA,
            capability="macro_analysis",
            agent_name=self.MACRO_AGENT,
            parameters=params,
            priority=TaskPriority.CRITICAL,
            planner_reasoning=(
                "Establish the macroeconomic environment."
            ),
        )

        market = self._create_task(
            title="Market Impact Analysis",
            description=(
                "Analyze how macroeconomic conditions affect "
                "financial markets and asset prices."
            ),
            task_type=TaskType.ANALYZE,
            capability="market_analysis",
            agent_name=self.MACRO_AGENT,
            parameters=params,
            dependencies=[
                macro.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Market impact requires the macroeconomic environment."
            ),
        )

        industry = self._create_task(
            title="Sector Impact Analysis",
            description=(
                "Analyze how macro conditions affect "
                "sectors and industries."
            ),
            task_type=TaskType.ANALYZE,
            capability="industry_analysis",
            agent_name=self.INDUSTRY_AGENT,
            parameters=params,
            dependencies=[
                macro.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Sector impact depends on the macroeconomic environment."
            ),
        )

        risks = self._create_task(
            title="Macro Risk Analysis",
            description=(
                "Identify key macroeconomic risks, scenarios, "
                "policy risks, and market vulnerabilities."
            ),
            task_type=TaskType.ANALYZE,
            capability="macro_risk_analysis",
            agent_name=self.RISK_AGENT,
            parameters=params,
            dependencies=[
                macro.id,
                market.id,
                industry.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Macro risks require macro, market, "
                "and sector analysis."
            ),
        )

        evidence = self._create_task(
            title="Validate Macro Evidence",
            description=(
                "Validate macroeconomic claims, data, assumptions, "
                "and supporting evidence."
            ),
            task_type=TaskType.VALIDATE,
            capability="evidence_validation",
            agent_name=self.EVIDENCE_AGENT,
            parameters=params,
            dependencies=[
                macro.id,
                market.id,
                industry.id,
                risks.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Validate the macro research before synthesis."
            ),
        )

        critic = self._create_task(
            title="Critique Macro Research",
            description=(
                "Critically evaluate the macro analysis, "
                "scenarios, assumptions, and evidence."
            ),
            task_type=TaskType.VALIDATE,
            capability="research_critique",
            agent_name=self.CRITIC_AGENT,
            parameters=params,
            dependencies=[
                evidence.id,
            ],
            priority=TaskPriority.HIGH,
            parallelizable=False,
            planner_reasoning=(
                "Critique the validated macro research."
            ),
        )

        report = self._create_task(
            title="Generate Macro Research Report",
            description=(
                "Generate the final macroeconomic research report."
            ),
            task_type=TaskType.GENERATE_REPORT,
            capability="research_report_generation",
            agent_name=self.INVESTMENT_COMMITTEE,
            parameters=params,
            dependencies=[
                critic.id,
            ],
            priority=TaskPriority.CRITICAL,
            parallelizable=False,
            planner_reasoning=(
                "Generate the final report after macro research "
                "validation and critique."
            ),
        )

        return [
            macro,
            market,
            industry,
            risks,
            evidence,
            critic,
            report,
        ]