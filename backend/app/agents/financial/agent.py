"""
app/agents/financial/agent.py

Financial Analysis Agent.

Performs financial analysis for equity research.

Canonical runtime architecture:

    ExecutionEngine
          |
          v
      AgentContext
          |
          v
        Worker
          |
          v
     AgentManager
          |
          v
    FinancialAnalysisAgent
          |
          v
  Financial Research Service
          |
          v
      AgentResult

IMPORTANT ARCHITECTURAL RULES

1. AgentContext is created upstream by ResearchService.

2. The SAME AgentContext instance travels through:

       ResearchService
            ↓
       ExecutionEngine
            ↓
       Dispatcher
            ↓
       Worker
            ↓
       AgentManager
            ↓
       BaseAgent
            ↓
       FinancialAnalysisAgent

3. FinancialAnalysisAgent MUST NOT create another AgentContext.

4. FinancialAnalysisAgent MUST NOT receive Task.

5. Task.agent_name is resolved by Worker / AgentManager.

6. FinancialAnalysisAgent receives runtime identity from:

       context.task_id
       context.task_type
       context.current_agent
       context.metadata

7. Canonical company identity comes from:

       context.company_id
       context.company
       context.ticker
       context.industry

8. Shared services come from:

       context.services

9. FinancialAnalysisAgent returns AgentResult.

10. AgentResult must be constructed through its canonical
    success() / failure() helpers.

11. Agent-specific dependencies must NOT be stored in
    application-global state.

12. FinancialAnalysisAgent must preserve the request-scoped
    AgentContext identity.

13. FinancialAnalysisAgent does not own database sessions.

14. FinancialAnalysisAgent does not construct repositories.

15. FinancialAnalysisAgent does not perform provider discovery
    directly.

16. FinancialAnalysisAgent delegates financial retrieval to
    FinancialResearchService.

17. The financial service receives the SAME AgentContext object.

18. Canonical company identity from AgentContext always wins over
    financial-service output.

19. FinancialAnalysisAgent MUST return AgentResult directly.
    It must never return a one-element tuple such as:

        return result,

    because that changes the canonical return type from AgentResult
    to tuple[AgentResult].
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.agents.base.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class FinancialAnalysisAgent(BaseAgent):
    """
    Performs financial analysis for the current research context.

    Canonical BaseAgent contract:

        run(context: AgentContext) -> AgentResult

    The Task object is intentionally NOT accepted here.

    Worker / AgentManager owns task routing and places the relevant
    runtime task identity into AgentContext before invoking this
    agent.
    """

    # =========================================================
    # Agent Identity
    # =========================================================

    agent_id = "financial"

    capabilities = [
        "financial.analysis",
    ]

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        services: AgentServices,
    ) -> None:
        """
        Initialize FinancialAnalysisAgent.

        AgentServices is supplied by AgentManager.

        The agent does not construct AgentServices itself.
        """

        if services is None:
            raise ValueError(
                "FinancialAnalysisAgent requires AgentServices."
            )

        if not isinstance(services, AgentServices):
            raise TypeError(
                "services must be an AgentServices instance, "
                f"got {type(services).__name__}."
            )

        super().__init__(
            services=services,
        )

    # =========================================================
    # Public Execution API
    # =========================================================

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute financial analysis using the canonical context.

        IMPORTANT:

        The exact AgentContext instance supplied by AgentManager
        is used throughout the operation.

        No Task is accepted.
        No AgentContext reconstruction occurs.
        No context dictionary is created.
        """

        # -----------------------------------------------------
        # Validate context
        # -----------------------------------------------------

        if not isinstance(context, AgentContext):
            raise TypeError(
                "FinancialAnalysisAgent requires an AgentContext."
            )

        # -----------------------------------------------------
        # Preserve exact context identity.
        #
        # This is the canonical request-scoped object.
        #
        # DO NOT:
        #
        #     AgentContext.from_dict(...)
        #
        # DO NOT:
        #
        #     AgentContext(...)
        #
        # DO NOT:
        #
        #     dict(context)
        # -----------------------------------------------------

        agent_context = context

        # -----------------------------------------------------
        # Runtime identity
        # -----------------------------------------------------

        research_id = agent_context.research_id
        task_id = agent_context.task_id
        task_type = agent_context.task_type
        current_agent = agent_context.current_agent

        # -----------------------------------------------------
        # Canonical company identity
        # -----------------------------------------------------

        company_id = agent_context.company_id
        company = agent_context.company
        ticker = agent_context.ticker
        industry = agent_context.industry

        # -----------------------------------------------------
        # Execution metadata
        # -----------------------------------------------------

        execution_id = agent_context.get_metadata(
            "execution_id"
        )

        trace_id = agent_context.get_metadata(
            "trace_id"
        )

        # =====================================================
        # Validate research identity
        # =====================================================

        if research_id is None:
            error = (
                "FinancialAnalysisAgent received an "
                "AgentContext without research_id."
            )

            logger.error(
                "%s | task_id=%r | context_object_id=%s",
                error,
                task_id,
                id(agent_context),
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=task_id,
                error=error,
            )

        # =====================================================
        # Validate task identity
        # =====================================================

        if not task_id:
            error = (
                "FinancialAnalysisAgent received an "
                "AgentContext without task_id."
            )

            logger.error(
                "%s | research_id=%r | context_object_id=%s",
                error,
                research_id,
                id(agent_context),
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=None,
                error=error,
            )

        # =====================================================
        # Validate company identity
        # =====================================================

        if not (
            company_id is not None
            or company
            or ticker
        ):
            error = (
                "FinancialAnalysisAgent received an "
                "AgentContext without canonical company identity."
            )

            logger.error(
                "%s | research_id=%r | task_id=%r | "
                "context_object_id=%s",
                error,
                research_id,
                task_id,
                id(agent_context),
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=task_id,
                error=error,
            )

        # =====================================================
        # Validate ticker
        # =====================================================

        # Financial providers normally require a ticker.
        #
        # We do not derive one from company name here because
        # company identity resolution belongs upstream.

        if not ticker:
            logger.warning(
                "FinancialAnalysisAgent received no ticker | "
                "research_id=%r | "
                "task_id=%r | "
                "company_id=%r | "
                "company=%r",
                research_id,
                task_id,
                company_id,
                company,
            )

        # =====================================================
        # Log canonical context
        # =====================================================

        logger.info(
            "FinancialAnalysisAgent started | "
            "research_id=%r | "
            "task_id=%r | "
            "task_type=%r | "
            "current_agent=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r | "
            "execution_id=%r | "
            "trace_id=%r | "
            "context_object_id=%s",
            research_id,
            task_id,
            task_type,
            current_agent,
            company_id,
            company,
            ticker,
            industry,
            execution_id,
            trace_id,
            id(agent_context),
        )

        # =====================================================
        # Resolve shared services
        # =====================================================

        try:
            services = agent_context.require_services()

        except Exception as exc:
            logger.exception(
                "FinancialAnalysisAgent services unavailable | "
                "research_id=%r | "
                "task_id=%r | "
                "context_object_id=%s",
                research_id,
                task_id,
                id(agent_context),
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=task_id,
                error=str(exc),
            )

        # =====================================================
        # Resolve FinancialResearchService
        # =====================================================

        financial_research = getattr(
            services,
            "financial_research",
            None,
        )

        if financial_research is None:
            error = (
                "AgentServices.financial_research is not configured."
            )

            logger.error(
                "%s | research_id=%r | task_id=%r",
                error,
                research_id,
                task_id,
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=task_id,
                error=error,
            )

        # =====================================================
        # Execute financial research
        # =====================================================

        try:
            logger.info(
                "FinancialAnalysisAgent invoking "
                "FinancialResearchService | "
                "research_id=%r | "
                "task_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "context_object_id=%s",
                research_id,
                task_id,
                company_id,
                company,
                ticker,
                id(agent_context),
            )

            financial_data = await self._get_financial_data(
                financial_research=financial_research,
                context=agent_context,
            )

            # -------------------------------------------------
            # Build stable agent result payload.
            # -------------------------------------------------

            result_data = self._build_result_data(
                context=agent_context,
                financial_data=financial_data,
            )

            logger.info(
                "FinancialAnalysisAgent completed | "
                "research_id=%r | "
                "task_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "context_object_id=%s",
                research_id,
                task_id,
                company_id,
                company,
                ticker,
                id(agent_context),
            )

            # IMPORTANT:
            #
            # Return AgentResult directly.
            #
            # CORRECT:
            #
            #     return AgentResult.success(...)
            #
            # INCORRECT:
            #
            #     return AgentResult.success(...),
            #
            # The latter creates:
            #
            #     tuple[AgentResult]
            #
            # which violates the BaseAgent contract.

            return AgentResult.success(
                agent_name=self.agent_id,
                task_id=task_id,
                data=result_data,
            )

        except Exception as exc:
            logger.exception(
                "FinancialAnalysisAgent failed | "
                "research_id=%r | "
                "task_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "context_object_id=%s",
                research_id,
                task_id,
                company_id,
                company,
                ticker,
                id(agent_context),
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=task_id,
                error=str(exc),
            )

    # =========================================================
    # Financial Service Invocation
    # =========================================================

    @staticmethod
    async def _get_financial_data(
        *,
        financial_research: Any,
        context: AgentContext,
    ) -> Any:
        """
        Invoke FinancialResearchService using the canonical
        AgentContext.

        The SAME AgentContext instance is passed to the service.

        No Task is constructed.
        No dictionary conversion occurs.

        Preferred service contract:

            await financial_research.get_financial_data(
                context=context
            )

        Compatibility methods are supported during migration:

            research(context=context)
            analyze(context=context)
        """

        if financial_research is None:
            raise ValueError(
                "financial_research service is required."
            )

        # =====================================================
        # Preferred API
        # =====================================================

        method = getattr(
            financial_research,
            "get_financial_data",
            None,
        )

        if callable(method):
            result = method(
                context=context,
            )

            if inspect.isawaitable(result):
                result = await result

            return result

        # =====================================================
        # Compatibility API: research()
        # =====================================================

        research_method = getattr(
            financial_research,
            "research",
            None,
        )

        if callable(research_method):
            result = research_method(
                context=context,
            )

            if inspect.isawaitable(result):
                result = await result

            return result

        # =====================================================
        # Compatibility API: analyze()
        # =====================================================

        analyze_method = getattr(
            financial_research,
            "analyze",
            None,
        )

        if callable(analyze_method):
            result = analyze_method(
                context=context,
            )

            if inspect.isawaitable(result):
                result = await result

            return result

        # =====================================================
        # Unsupported API
        # =====================================================

        raise AttributeError(
            "FinancialResearchService does not expose a "
            "supported context-based financial research method. "
            "Expected one of: "
            "get_financial_data(), research(), analyze()."
        )

    # =========================================================
    # Result Construction
    # =========================================================

    @staticmethod
    def _build_result_data(
        *,
        context: AgentContext,
        financial_data: Any,
    ) -> dict[str, Any]:
        """
        Build the FinancialAnalysisAgent result payload.

        Canonical company identity ALWAYS comes from AgentContext.

        FinancialResearchService output is preserved under
        "financial_data".

        If the service returns a dictionary, its fields are also
        exposed at the result level for compatibility.

        Canonical identity is re-applied after merging service
        output so external/service data cannot overwrite it.
        """

        # -----------------------------------------------------
        # Start with canonical identity.
        # -----------------------------------------------------

        result: dict[str, Any] = {
            "research_id": context.research_id,
            "company_id": context.company_id,
            "company": context.company,
            "ticker": context.ticker,
            "industry": context.industry,
            "financial_data": financial_data,
        }

        # -----------------------------------------------------
        # Preserve service fields.
        # -----------------------------------------------------

        if isinstance(financial_data, dict):
            result.update(financial_data)

        # -----------------------------------------------------
        # Canonical identity ALWAYS wins.
        # -----------------------------------------------------

        result["research_id"] = context.research_id

        result["company_id"] = context.company_id

        result["company"] = context.company

        result["ticker"] = context.ticker

        result["industry"] = context.industry

        # -----------------------------------------------------
        # Preserve complete service result.
        # -----------------------------------------------------

        result["financial_data"] = financial_data

        return result