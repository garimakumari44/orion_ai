"""
app/agents/company/agent.py

Company Research Agent.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.agents.base.base_agent import BaseAgent

from app.agents.company.analyzer import CompanyAnalyzer
from app.agents.company.prompt import (
    COMPANY_ANALYSIS_PROMPT,
    COMPANY_RESEARCH_SYSTEM_PROMPT,
)


logger = logging.getLogger(__name__)


class CompanyAgent(BaseAgent):

    agent_id = "company"

    category = "research"

    display_name = "Company Research Agent"

    description = (
        "Performs deep company research for equity analysis. "
        "Retrieves and structures company information and "
        "generates company insights."
    )

    capabilities = [
        "company.research",
    ]

    def __init__(
        self,
        services: AgentServices,
    ) -> None:
        """
        Initialize CompanyAgent.

        AgentManager injects the canonical AgentServices.
        """

        super().__init__(
            services=services,
        )

        self.analyzer = CompanyAnalyzer()

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:

        try:

            # =================================================
            # 1. Validate context
            # =================================================

            if context is None:
                raise ValueError(
                    "AgentContext is required for CompanyAgent"
                )

            # =================================================
            # 2. Canonical identity
            # =================================================

            research_id = context.research_id

            company_id = context.company_id

            company = context.company

            ticker = context.ticker

            industry = context.industry

            # =================================================
            # 3. Task identity
            # =================================================

            task_id = context.task_id

            task_type = context.task_type

            assigned_executor = (
                context.assigned_executor
            )

            # =================================================
            # 4. Research metadata
            # =================================================

            query = context.get_query()

            intent = context.get_intent()

            research_type = context.get_research_type()

            # =================================================
            # 5. Request-scoped repository
            # =================================================
            #
            # This is intentionally NOT obtained from
            # context.metadata.
            #
            # It is the actual request-scoped repository
            # injected by ResearchService.
            # =================================================

            repository = (
                context.require_company_repository()
            )

            # =================================================
            # 6. Shared services
            # =================================================

            services = context.require_services()

            # =================================================
            # 7. Supplemental metadata
            # =================================================

            metadata: dict[str, Any] = {}

            if isinstance(
                context.metadata,
                dict,
            ):
                metadata = dict(
                    context.metadata
                )

            logger.info(
                "COMPANY AGENT START | "
                "context_object_id=%s | "
                "services_object_id=%s | "
                "company_repository_id=%s | "
                "task_id=%r | "
                "task_type=%r | "
                "assigned_executor=%r | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "industry=%r",
                id(context),
                id(services),
                id(repository),
                task_id,
                task_type,
                assigned_executor,
                research_id,
                company_id,
                company,
                ticker,
                industry,
            )

            # =================================================
            # 8. Validate research identity
            # =================================================

            if research_id is None:
                raise ValueError(
                    "research_id missing from AgentContext"
                )

            # =================================================
            # 9. Validate company identity
            # =================================================

            if company_id is None:
                raise ValueError(
                    "company_id missing from AgentContext | "
                    f"research_id={research_id!r}"
                )

            if not company and not ticker:
                raise ValueError(
                    "Company data missing from AgentContext | "
                    f"research_id={research_id!r} | "
                    f"company_id={company_id!r} | "
                    f"company={company!r} | "
                    f"ticker={ticker!r}"
                )

            # =================================================
            # 10. Seed company data
            # =================================================

            seed_company_data: dict[str, Any] = {
                "research_id": research_id,

                "company_id": company_id,

                "company": company,

                "company_name": company,

                "ticker": ticker,

                "industry": industry,

                "query": query,

                "user_query": query,

                "intent": intent,

                "research_type": research_type,

                "metadata": metadata,
            }

            # =================================================
            # 11. Resolve company research service
            # =================================================

            research_service = getattr(
                services,
                "company_research",
                None,
            )

            if research_service is None:
                raise RuntimeError(
                    "Company research service is not configured "
                    "in AgentServices. Expected "
                    "services.company_research."
                )

            # =================================================
            # 12. Company enrichment
            # =================================================

            logger.info(
                "COMPANY AGENT → COMPANY RESEARCH SERVICE | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "repository_id=%s",
                research_id,
                company_id,
                company,
                ticker,
                id(repository),
            )

            enriched_company_data = (
                await research_service.research(
                    company_data=seed_company_data,
                    repository=repository,
                )
            )

            # =================================================
            # 13. Validate response
            # =================================================

            if not isinstance(
                enriched_company_data,
                dict,
            ):
                raise TypeError(
                    "Company research service must return "
                    "a dict. "
                    f"Received: "
                    f"{type(enriched_company_data).__name__}"
                )

            # =================================================
            # 14. Preserve canonical identity
            # =================================================

            enriched_company_data = {
                **enriched_company_data,

                "research_id": research_id,

                "company_id": company_id,

                "company": company,

                "company_name": company,

                "ticker": ticker,

                "industry": industry,

                "query": query,

                "user_query": query,

                "intent": intent,

                "research_type": research_type,

                "metadata": metadata,
            }

            # =================================================
            # 15. Validate canonical identity
            # =================================================

            if enriched_company_data.get(
                "research_id"
            ) != research_id:
                raise RuntimeError(
                    "Company enrichment corrupted "
                    "research_id"
                )

            if enriched_company_data.get(
                "company_id"
            ) != company_id:
                raise RuntimeError(
                    "Company enrichment corrupted "
                    "company_id"
                )

            if company and (
                enriched_company_data.get(
                    "company"
                )
                != company
            ):
                raise RuntimeError(
                    "Company enrichment corrupted "
                    "company identity"
                )

            if ticker and (
                enriched_company_data.get(
                    "ticker"
                )
                != ticker
            ):
                raise RuntimeError(
                    "Company enrichment corrupted "
                    "ticker identity"
                )

            # =================================================
            # 16. Store enrichment in context
            # =================================================

            context.set_data(
                "company",
                enriched_company_data,
            )

            context.set_data(
                "company_research",
                enriched_company_data,
            )

            # =================================================
            # 17. Deterministic analysis
            # =================================================

            deterministic_analysis = (
                self.analyzer.analyze(
                    company_data=enriched_company_data,
                )
            )

            context.set_data(
                "company_analysis",
                deterministic_analysis,
            )

            # =================================================
            # 18. Build LLM prompt
            # =================================================

            llm_prompt = COMPANY_ANALYSIS_PROMPT.format(
                company_name=(
                    enriched_company_data.get(
                        "company_name"
                    )
                ),
                company_data=enriched_company_data,
                deterministic_analysis=(
                    deterministic_analysis
                ),
            )

            # =================================================
            # 19. LLM analysis
            # =================================================

            llm_analysis = services.llm.generate(
                prompt=llm_prompt,
                system_prompt=(
                    COMPANY_RESEARCH_SYSTEM_PROMPT
                ),
            )

            context.set_data(
                "company_llm_analysis",
                llm_analysis,
            )

            # =================================================
            # 20. Final result
            # =================================================

            result = {
                "company_data": seed_company_data,

                "enriched_company_data": (
                    enriched_company_data
                ),

                "deterministic_analysis": (
                    deterministic_analysis
                ),

                "research_analysis": llm_analysis,

                "research_id": research_id,

                "company_id": company_id,

                "company": company,

                "ticker": ticker,

                "industry": industry,
            }

            logger.info(
                "COMPANY RESEARCH COMPLETED | "
                "task_id=%r | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "context_object_id=%s | "
                "repository_id=%s",
                task_id,
                research_id,
                company_id,
                company,
                ticker,
                id(context),
                id(repository),
            )

            return AgentResult.success(
                agent_name=self.agent_id,
                task_id=task_id,
                data=result,
            )

        except Exception as exc:

            logger.exception(
                "COMPANY AGENT FAILED | "
                "exception_type=%s | "
                "exception=%s",
                type(exc).__name__,
                str(exc),
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=(
                    context.task_id
                    if context is not None
                    else None
                ),
                error=str(exc),
            )