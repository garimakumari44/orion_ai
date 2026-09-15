"""
app/agents/base/agent_context.py

Canonical Runtime Context.

ONE AgentContext instance is created for one research execution
and propagated unchanged through:

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
Specialized Agent

Architectural rules
-------------------

1. AgentContext is identity-preserving.
2. Existing AgentContext objects are never cloned.
3. Worker/Dispatcher/AgentManager must not reconstruct context.
4. Task.agent_name is the canonical agent-routing field.
5. assigned_executor is legacy compatibility only.
6. company_repository is request-scoped infrastructure.
7. company_repository must never live inside AgentServices.
8. ExecutionEngine owns execution_id.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.repositories.company_repository import CompanyRepository


@dataclass
class AgentContext:
    """Canonical runtime state shared by all agents."""

    # =========================================================
    # Research identity
    # =========================================================

    research_id: int | str | None = None
    research_type: str | None = None

    # =========================================================
    # Task identity
    # =========================================================

    task_id: str | None = None
    task_type: str | None = None

    # Legacy compatibility only.
    assigned_executor: str | None = None

    # =========================================================
    # User / request identity
    # =========================================================

    user_id: int | str | None = None
    query: str | None = None
    user_query: str | None = None
    intent: str | None = None

    # =========================================================
    # Company identity
    #
    # IMPORTANT:
    # These fields represent canonical company identity for
    # the current research execution.
    #
    # Industry MUST be propagated here by ResearchService.
    # Specialized agents must not rediscover it.
    # =========================================================

    company_id: int | None = None
    company: str | None = None
    ticker: str | None = None
    industry: str | None = None

    companies: list[dict[str, Any]] = field(
        default_factory=list
    )

    # =========================================================
    # Portfolio
    # =========================================================

    portfolio: (
        dict[str, Any]
        | list[dict[str, Any]]
        | None
    ) = None

    # =========================================================
    # Runtime input
    # =========================================================

    data: dict[str, Any] = field(
        default_factory=dict
    )

    parameters: dict[str, Any] = field(
        default_factory=dict
    )

    # =========================================================
    # Workflow tracking
    # =========================================================

    workflow_id: str | None = None
    current_agent: str | None = None

    # Legacy execution compatibility.
    current_task_id: str | None = None

    # =========================================================
    # Shared services
    # =========================================================

    services: AgentServices | None = None

    # =========================================================
    # Request-scoped repository
    # =========================================================

    company_repository: CompanyRepository | None = None

    # =========================================================
    # Shared execution state
    # =========================================================

    knowledge: dict[str, Any] = field(
        default_factory=dict
    )

    memory: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # =========================================================
    # Agent outputs
    # =========================================================

    agent_results: dict[str, AgentResult] = field(
        default_factory=dict
    )

    # =========================================================
    # Research evidence
    # =========================================================

    evidence: list[dict[str, Any]] = field(
        default_factory=list
    )

    citations: list[str] = field(
        default_factory=list
    )

    # =========================================================
    # Construction
    # =========================================================

    @classmethod
    def from_dict(
        cls,
        context: dict[str, Any] | AgentContext | None,
    ) -> AgentContext:
        """
        Normalize a context at an external boundary.

        IMPORTANT
        ---------

        If context is already an AgentContext, the exact same
        object is returned.

        This method must NOT be used by the canonical execution
        path to reconstruct the runtime context.
        """

        if context is None:
            return cls()

        # =====================================================
        # CRITICAL IDENTITY RULE
        # =====================================================

        if isinstance(context, cls):
            return context

        if not isinstance(context, dict):
            raise TypeError(
                "context must be a dictionary or AgentContext"
            )

        values = dict(context)

        # =====================================================
        # Metadata
        # =====================================================

        metadata = values.get("metadata")

        if metadata is None:
            metadata = {}

        elif not isinstance(metadata, dict):
            raise TypeError(
                "AgentContext.metadata must be a dictionary"
            )

        else:
            metadata = dict(metadata)

        # =====================================================
        # Legacy metadata normalization
        # =====================================================

        for key in (
            "query",
            "intent",
            "research_type",
            "user_id",
            "task_id",
            "task_type",
            "assigned_executor",
            "company_id",
        ):
            if key in values and key not in metadata:
                metadata[key] = values[key]

        # =====================================================
        # Research ID
        # =====================================================

        research_id = values.get("research_id")

        if research_id is not None and not isinstance(
            research_id,
            (int, str),
        ):
            raise TypeError(
                "AgentContext.research_id must be int, str, or None"
            )

        values["research_id"] = research_id

        # =====================================================
        # Task identity
        # =====================================================

        task_id = (
            values.get("task_id")
            or values.get("current_task_id")
            or metadata.get("task_id")
        )

        if task_id is not None:
            task_id = str(task_id)

        values["task_id"] = task_id

        values["current_task_id"] = (
            task_id
            if task_id is not None
            else values.get("current_task_id")
        )

        task_type = (
            values.get("task_type")
            or metadata.get("task_type")
        )

        values["task_type"] = (
            str(task_type)
            if task_type is not None
            else None
        )

        assigned_executor = (
            values.get("assigned_executor")
            or metadata.get("assigned_executor")
        )

        values["assigned_executor"] = (
            str(assigned_executor)
            if assigned_executor is not None
            else None
        )

        # =====================================================
        # User identity
        # =====================================================

        user_id = (
            values.get("user_id")
            if values.get("user_id") is not None
            else metadata.get("user_id")
        )

        if isinstance(user_id, bool):
            raise TypeError(
                "AgentContext.user_id must be int, str, or None"
            )

        if user_id is not None and not isinstance(
            user_id,
            (int, str),
        ):
            raise TypeError(
                "AgentContext.user_id must be int, str, or None"
            )

        values["user_id"] = user_id

        # =====================================================
        # Company normalization
        # =====================================================

        company_value = values.get("company")

        if isinstance(company_value, dict):
            company_data = dict(company_value)

            values["company"] = (
                company_data.get("name")
                or company_data.get("company")
                or company_data.get("company_name")
                or company_data.get("legal_name")
            )

            if values.get("company_id") is None:
                values["company_id"] = (
                    company_data.get("id")
                    or company_data.get("company_id")
                )

            if not values.get("ticker"):
                values["ticker"] = (
                    company_data.get("ticker")
                    or company_data.get("symbol")
                    or company_data.get("stock_symbol")
                )

            # IMPORTANT:
            #
            # Do NOT use sector as industry.
            #
            # sector and industry are distinct concepts.
            #
            # Canonical industry must come from:
            #
            # Company.industry
            #
            # or an explicit sub_industry field.
            if not values.get("industry"):
                values["industry"] = (
                    company_data.get("industry")
                    or company_data.get("sub_industry")
                )

        elif company_value is not None and not isinstance(
            company_value,
            str,
        ):
            raise TypeError(
                "AgentContext.company must be string, dict, or None"
            )

        # =====================================================
        # Company ID
        # =====================================================

        company_id = (
            values.get("company_id")
            if values.get("company_id") is not None
            else metadata.get("company_id")
        )

        if isinstance(company_id, bool):
            raise TypeError(
                "AgentContext.company_id must be an integer or None"
            )

        if isinstance(company_id, str):
            try:
                company_id = int(company_id)

            except ValueError as exc:
                raise TypeError(
                    "AgentContext.company_id must be an integer or None"
                ) from exc

        if company_id is not None and not isinstance(
            company_id,
            int,
        ):
            raise TypeError(
                "AgentContext.company_id must be an integer or None"
            )

        values["company_id"] = company_id

        if company_id is not None:
            metadata["company_id"] = company_id

        # =====================================================
        # Ticker / Industry
        # =====================================================

        for field_name in (
            "ticker",
            "industry",
        ):
            value = values.get(field_name)

            if value is not None and not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"AgentContext.{field_name} must be "
                    "string or None"
                )

            if isinstance(value, str):
                value = value.strip()

                values[field_name] = (
                    value
                    if value
                    else None
                )

        # =====================================================
        # Query
        # =====================================================

        query = (
            values.get("query")
            or values.get("user_query")
            or metadata.get("query")
        )

        values["query"] = (
            str(query)
            if query is not None
            else None
        )

        values["user_query"] = (
            values["query"]
            if values.get("user_query") is None
            else str(values["user_query"])
        )

        # =====================================================
        # Intent
        # =====================================================

        intent = (
            values.get("intent")
            or metadata.get("intent")
        )

        values["intent"] = (
            str(intent)
            if intent is not None
            else None
        )

        # =====================================================
        # Research type
        # =====================================================

        research_type = (
            values.get("research_type")
            or metadata.get("research_type")
        )

        values["research_type"] = (
            str(research_type)
            if research_type is not None
            else None
        )

        # =====================================================
        # Collection normalization
        # =====================================================

        companies = values.get("companies")

        if companies is None:
            companies = []

        elif not isinstance(companies, list):
            raise TypeError(
                "AgentContext.companies must be a list"
            )

        else:
            companies = list(companies)

        values["companies"] = companies

        portfolio = values.get("portfolio")

        if portfolio is not None and not isinstance(
            portfolio,
            (dict, list),
        ):
            raise TypeError(
                "AgentContext.portfolio must be dict, list, or None"
            )

        values["portfolio"] = portfolio

        # =====================================================
        # Dictionary state
        # =====================================================

        for field_name in (
            "data",
            "parameters",
            "knowledge",
            "memory",
        ):
            value = values.get(field_name)

            if value is None:
                values[field_name] = {}

            elif not isinstance(value, dict):
                raise TypeError(
                    f"AgentContext.{field_name} must be a dictionary"
                )

            else:
                values[field_name] = dict(value)

        # =====================================================
        # Agent results
        # =====================================================

        agent_results = values.get("agent_results")

        if agent_results is None:
            values["agent_results"] = {}

        elif not isinstance(agent_results, dict):
            raise TypeError(
                "AgentContext.agent_results must be a dictionary"
            )

        else:
            values["agent_results"] = dict(agent_results)

        # =====================================================
        # Evidence / citations
        # =====================================================

        evidence = values.get("evidence")

        if evidence is None:
            values["evidence"] = []

        elif not isinstance(evidence, list):
            raise TypeError(
                "AgentContext.evidence must be a list"
            )

        else:
            values["evidence"] = list(evidence)

        citations = values.get("citations")

        if citations is None:
            values["citations"] = []

        elif not isinstance(citations, list):
            raise TypeError(
                "AgentContext.citations must be a list"
            )

        else:
            values["citations"] = list(citations)

        # =====================================================
        # Runtime dependencies
        # =====================================================

        services = values.get("services")

        if services is not None and not isinstance(
            services,
            AgentServices,
        ):
            raise TypeError(
                "AgentContext.services must be "
                "AgentServices or None"
            )

        repository = values.get(
            "company_repository"
        )

        if repository is not None and not isinstance(
            repository,
            CompanyRepository,
        ):
            raise TypeError(
                "AgentContext.company_repository must be "
                "CompanyRepository or None"
            )

        values["metadata"] = metadata

        # =====================================================
        # Remove unknown external fields
        # =====================================================

        allowed_fields = {
            "research_id",
            "research_type",
            "task_id",
            "task_type",
            "assigned_executor",
            "user_id",
            "query",
            "user_query",
            "intent",
            "company_id",
            "company",
            "ticker",
            "industry",
            "companies",
            "portfolio",
            "data",
            "parameters",
            "workflow_id",
            "current_agent",
            "current_task_id",
            "services",
            "company_repository",
            "knowledge",
            "memory",
            "metadata",
            "agent_results",
            "evidence",
            "citations",
        }

        normalized = {
            key: value
            for key, value in values.items()
            if key in allowed_fields
        }

        return cls(**normalized)

    # =========================================================
    # Results
    # =========================================================

    def add_result(
        self,
        result: AgentResult,
    ) -> None:

        if not isinstance(
            result,
            AgentResult,
        ):
            raise TypeError(
                "result must be an AgentResult"
            )

        agent_name = getattr(
            result,
            "agent_name",
            None,
        )

        if not agent_name:
            raise ValueError(
                "AgentResult.agent_name cannot be empty"
            )

        self.agent_results[
            str(agent_name)
        ] = result

    def get_result(
        self,
        agent_name: str,
    ) -> AgentResult | None:

        if not agent_name:
            return None

        return self.agent_results.get(
            agent_name
        )

    def get_result_data(
        self,
        agent_name: str,
        default: Any = None,
    ) -> Any:

        result = self.get_result(
            agent_name
        )

        if result is None:
            return default

        return getattr(
            result,
            "data",
            default,
        )

    def has_result(
        self,
        agent_name: str,
    ) -> bool:

        return bool(
            agent_name
            and agent_name in self.agent_results
        )

    # =========================================================
    # Knowledge
    # =========================================================

    def update_knowledge(
        self,
        key: str,
        value: Any,
    ) -> None:

        if not key:
            raise ValueError(
                "Knowledge key cannot be empty"
            )

        self.knowledge[key] = value

    def get_knowledge(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.knowledge.get(
            key,
            default,
        )

    # =========================================================
    # Evidence / citations
    # =========================================================

    def add_evidence(
        self,
        item: dict[str, Any],
    ) -> None:

        if not isinstance(
            item,
            dict,
        ):
            raise TypeError(
                "Evidence must be a dictionary"
            )

        self.evidence.append(
            dict(item)
        )

    def add_citation(
        self,
        citation: str,
    ) -> None:

        if citation and citation not in self.citations:
            self.citations.append(
                citation
            )

    # =========================================================
    # Runtime data
    # =========================================================

    def set_data(
        self,
        key: str,
        value: Any,
    ) -> None:

        if not key:
            raise ValueError(
                "Data key cannot be empty"
            )

        self.data[key] = value

    def get_data(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.data.get(
            key,
            default,
        )

    # =========================================================
    # Memory
    # =========================================================

    def set_memory(
        self,
        key: str,
        value: Any,
    ) -> None:

        if not key:
            raise ValueError(
                "Memory key cannot be empty"
            )

        self.memory[key] = value

    def get_memory(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.memory.get(
            key,
            default,
        )

    # =========================================================
    # Task tracking
    # =========================================================

    def set_task(
        self,
        task_id: str | int | None,
        task_type: str | None = None,
        assigned_executor: str | None = None,
    ) -> None:
        """
        Set the currently executing task.

        task_id/task_type are canonical task identity.

        assigned_executor is retained only for compatibility.
        """

        if task_id is None:
            self.clear_task()
            return

        normalized_task_id = str(
            task_id
        )

        self.task_id = normalized_task_id

        self.current_task_id = (
            normalized_task_id
        )

        self.metadata[
            "task_id"
        ] = normalized_task_id

        self.task_type = (
            str(task_type)
            if task_type is not None
            else None
        )

        if self.task_type is None:
            self.metadata.pop(
                "task_type",
                None,
            )

        else:
            self.metadata[
                "task_type"
            ] = self.task_type

        self.assigned_executor = (
            str(assigned_executor)
            if assigned_executor is not None
            else None
        )

        if self.assigned_executor is None:
            self.metadata.pop(
                "assigned_executor",
                None,
            )

        else:
            self.metadata[
                "assigned_executor"
            ] = self.assigned_executor

    def clear_task(self) -> None:

        self.task_id = None
        self.task_type = None
        self.assigned_executor = None
        self.current_task_id = None

        for key in (
            "task_id",
            "task_type",
            "assigned_executor",
            "task_metadata",
        ):
            self.metadata.pop(
                key,
                None,
            )

    def set_current_task(
        self,
        task_id: str | int | None,
    ) -> None:

        self.set_task(
            task_id
        )

    # =========================================================
    # Agent tracking
    # =========================================================

    def set_current_agent(
        self,
        agent_name: str | None,
    ) -> None:

        normalized = (
            str(agent_name)
            if agent_name is not None
            else None
        )

        self.current_agent = normalized

        if normalized is None:
            self.metadata.pop(
                "agent_name",
                None,
            )

        else:
            self.metadata[
                "agent_name"
            ] = normalized

    # =========================================================
    # Workflow
    # =========================================================

    def set_workflow(
        self,
        workflow_id: str | None,
    ) -> None:

        self.workflow_id = (
            str(workflow_id)
            if workflow_id is not None
            else None
        )

    # =========================================================
    # Parameters
    # =========================================================

    def set_parameter(
        self,
        key: str,
        value: Any,
    ) -> None:

        if not key:
            raise ValueError(
                "Parameter key cannot be empty"
            )

        self.parameters[key] = value

    def get_parameter(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.parameters.get(
            key,
            default,
        )

    # =========================================================
    # Metadata
    # =========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        if not key:
            raise ValueError(
                "Metadata key cannot be empty"
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )

    # =========================================================
    # Research helpers
    # =========================================================

    def get_query(self) -> str | None:

        if self.query:
            return self.query

        if self.user_query:
            return self.user_query

        value = self.metadata.get(
            "query"
        )

        return (
            value
            if isinstance(value, str)
            else None
        )

    def get_intent(self) -> str | None:

        if self.intent:
            return self.intent

        value = self.metadata.get(
            "intent"
        )

        return (
            str(value)
            if value is not None
            else None
        )

    def get_research_type(self) -> str | None:

        if self.research_type:
            return self.research_type

        value = self.metadata.get(
            "research_type"
        )

        return (
            str(value)
            if value is not None
            else None
        )

    # =========================================================
    # Company
    # =========================================================

    def has_company(self) -> bool:

        return bool(
            self.company
            or self.ticker
            or self.company_id
        )

    def set_company(
        self,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        company_id: int | str | None = None,
    ) -> None:

        if company_id is not None:

            if isinstance(
                company_id,
                bool,
            ):
                raise TypeError(
                    "company_id must be an integer or None"
                )

            if isinstance(
                company_id,
                str,
            ):
                try:
                    company_id = int(
                        company_id
                    )

                except ValueError as exc:
                    raise TypeError(
                        "company_id must be an integer or None"
                    ) from exc

            if not isinstance(
                company_id,
                int,
            ):
                raise TypeError(
                    "company_id must be an integer or None"
                )

            self.company_id = company_id

            self.metadata[
                "company_id"
            ] = company_id

        if company is not None:

            if not isinstance(
                company,
                str,
            ):
                raise TypeError(
                    "company must be a string or None"
                )

            self.company = company.strip()

        if ticker is not None:

            if not isinstance(
                ticker,
                str,
            ):
                raise TypeError(
                    "ticker must be a string or None"
                )

            self.ticker = ticker.strip()

        if industry is not None:

            if not isinstance(
                industry,
                str,
            ):
                raise TypeError(
                    "industry must be a string or None"
                )

            self.industry = industry.strip()

    # =========================================================
    # Companies
    # =========================================================

    def add_company(
        self,
        company: dict[str, Any],
    ) -> None:

        if not isinstance(
            company,
            dict,
        ):
            raise TypeError(
                "company must be a dictionary"
            )

        self.companies.append(
            dict(company)
        )

    def get_companies(
        self,
    ) -> list[dict[str, Any]]:

        return self.companies

    # =========================================================
    # Portfolio
    # =========================================================

    def set_portfolio(
        self,
        portfolio: (
            dict[str, Any]
            | list[dict[str, Any]]
            | None
        ),
    ) -> None:

        if portfolio is not None and not isinstance(
            portfolio,
            (dict, list),
        ):
            raise TypeError(
                "portfolio must be dict, list, or None"
            )

        self.portfolio = portfolio

    # =========================================================
    # Services
    # =========================================================

    def set_services(
        self,
        services: AgentServices,
    ) -> None:

        if not isinstance(
            services,
            AgentServices,
        ):
            raise TypeError(
                "services must be an AgentServices instance"
            )

        self.services = services

    def require_services(
        self,
    ) -> AgentServices:

        if self.services is None:
            raise RuntimeError(
                "AgentContext.services is not configured"
            )

        return self.services

    # =========================================================
    # Company repository
    # =========================================================

    def set_company_repository(
        self,
        repository: CompanyRepository,
    ) -> None:

        if not isinstance(
            repository,
            CompanyRepository,
        ):
            raise TypeError(
                "repository must be a CompanyRepository instance"
            )

        self.company_repository = repository

    def require_company_repository(
        self,
    ) -> CompanyRepository:

        if self.company_repository is None:
            raise RuntimeError(
                "AgentContext.company_repository is not configured"
            )

        return self.company_repository

    # =========================================================
    # Debug
    # =========================================================

    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "context_object_id": id(self),
            "research_id": self.research_id,
            "research_type": self.get_research_type(),
            "task_id": self.task_id,
            "task_type": self.task_type,
            "assigned_executor": self.assigned_executor,
            "current_task_id": self.current_task_id,
            "user_id": self.user_id,
            "query": self.get_query(),
            "intent": self.get_intent(),
            "company_id": self.company_id,
            "company": self.company,
            "ticker": self.ticker,
            "industry": self.industry,
            "company_count": len(
                self.companies
            ),
            "has_portfolio": (
                self.portfolio is not None
            ),
            "workflow_id": self.workflow_id,
            "current_agent": self.current_agent,
            "parameter_keys": list(
                self.parameters
            ),
            "data_keys": list(
                self.data
            ),
            "knowledge_keys": list(
                self.knowledge
            ),
            "memory_keys": list(
                self.memory
            ),
            "agent_result_count": len(
                self.agent_results
            ),
            "agent_names": list(
                self.agent_results
            ),
            "evidence_count": len(
                self.evidence
            ),
            "citation_count": len(
                self.citations
            ),
            "services_configured": (
                self.services is not None
            ),
            "company_repository_configured": (
                self.company_repository is not None
            ),
        }

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(
        self,
        *,
        include_runtime_state: bool = True,
    ) -> dict[str, Any]:
        """
        Serialize logical context state.

        Live AgentServices and CompanyRepository instances are
        intentionally excluded.

        This dictionary is for persistence/debug/external
        boundaries only.

        It must NOT be used to reconstruct the context inside
        the canonical execution pipeline.
        """

        result: dict[str, Any] = {
            "research_id": self.research_id,
            "research_type": self.research_type,

            "task_id": self.task_id,
            "task_type": self.task_type,
            "assigned_executor": self.assigned_executor,

            "user_id": self.user_id,
            "query": self.query,
            "user_query": self.user_query,
            "intent": self.intent,

            "company_id": self.company_id,
            "company": self.company,
            "ticker": self.ticker,
            "industry": self.industry,

            "companies": list(
                self.companies
            ),

            "portfolio": self.portfolio,

            "data": dict(
                self.data
            ),

            "parameters": dict(
                self.parameters
            ),

            "workflow_id": self.workflow_id,
            "current_agent": self.current_agent,
            "current_task_id": self.current_task_id,

            "knowledge": dict(
                self.knowledge
            ),

            "memory": dict(
                self.memory
            ),

            "metadata": dict(
                self.metadata
            ),

            "agent_results": {
                name: (
                    value.to_dict()
                    if hasattr(
                        value,
                        "to_dict",
                    )
                    else value
                )
                for name, value in (
                    self.agent_results.items()
                )
            },

            "evidence": list(
                self.evidence
            ),

            "citations": list(
                self.citations
            ),
        }

        if not include_runtime_state:
            result.pop(
                "current_agent",
                None,
            )

            result.pop(
                "current_task_id",
                None,
            )

            result.pop(
                "agent_results",
                None,
            )

        return result