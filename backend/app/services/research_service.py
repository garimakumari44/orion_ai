""" 
app/services/research_service.py 
 
Application-level orchestration service for research execution. 
 
Architecture 
------------ 
 
    ResearchService 
        | 
        +--> resolve Research 
        | 
        +--> resolve canonical Company 
        | 
        +--> resolve canonical Industry 
        | 
        +--> create ONE AgentContext 
        | 
        +--> ExecutionEngine 
        | 
        +--> normalize execution results 
        | 
        +--> persist ResearchResult 
        | 
        +--> expose persisted results 
 
 
Canonical final research result storage: 
 
    research_results 
 
 
Lifecycle/progress metadata: 
 
    research.metadata_json 
 
 
IMPORTANT ARCHITECTURAL RULE 
---------------------------- 
 
Canonical company identity is: 
 
    company_id 
    company 
    ticker 
    industry 
 
Industry is distinct from sector. 
 
The backend MUST NEVER map: 
 
    Company.sector -> industry 
 
ResearchResult is the canonical source for completed research output. 
 
research.metadata_json is ONLY lifecycle/context metadata. 
It must never be treated as the canonical research-result store. 
""" 
 
from __future__ import annotations 
 
import logging 
import math 
 
from dataclasses import asdict, is_dataclass 
from datetime import date, datetime, time, timezone 
from decimal import Decimal 
from enum import Enum 
from typing import Any 
from uuid import UUID 
 
from sqlalchemy.ext.asyncio import AsyncSession 
 
from app.agents.base.agent_context import AgentContext 
from app.agents.base.agent_services import AgentServices 
 
from app.execution.execution_engine import ExecutionEngine 
 
from app.services.industry_catalog_service import ( 
    IndustryCatalogService, 
) 
 
from app.db.models.research import Research 
from app.db.models.research_result import ResearchResult 
 
from app.planning.models.execution_plan import ExecutionPlan 
from app.planning.parser import PlanningParser 
from app.planning.planner import Planner 
 
from app.repositories.company_repository import CompanyRepository 
from app.repositories.research_repository import ResearchRepository 
from app.repositories.research_result_repository import ( 
    ResearchResultRepository, 
) 
 
from app.schemas.research import ( 
    ResearchDocument, 
    ResearchEvidence, 
    ResearchInsight, 
    ResearchOverview, 
    ResearchProfile, 
    ResearchReport, 
    ResearchReportSection, 
    ResearchResultResponse, 
    ResearchStartRequest, 
    ResearchStartResponse, 
    ResearchStatusResponse, 
    ResearchSummary, 
) 
 
 
logger = logging.getLogger(__name__) 
 
 
class ResearchService: 
    """ 
    Application-level research orchestration service. 
 
    Responsibilities 
    ---------------- 
 
    - Parse research requests. 
    - Build execution plans. 
    - Resolve canonical company identity. 
    - Resolve canonical industry. 
    - Create Research records. 
    - Create exactly one AgentContext. 
    - Execute the research plan. 
    - Normalize execution results. 
    - Persist ResearchResult. 
    - Manage research lifecycle state. 
    - Expose persisted research results. 
 
    This class does NOT use Company.sector as industry. 
    """ 
 
    # ============================================================ 
    # Initialization 
    # ============================================================ 
 
    def __init__( 
        self, 
        db: AsyncSession, 
        company_repository: CompanyRepository, 
        industry_catalog_service: IndustryCatalogService, 
        parser: PlanningParser, 
        planner: Planner, 
        execution_engine: ExecutionEngine, 
        services: AgentServices, 
    ) -> None: 
 
        if db is None: 
            raise ValueError("AsyncSession is required.") 
 
        if company_repository is None: 
            raise ValueError( 
                "CompanyRepository is required." 
            ) 
 
        if not isinstance( 
            company_repository, 
            CompanyRepository, 
        ): 
            raise TypeError( 
                "company_repository must be a " 
                "CompanyRepository instance." 
            ) 
 
        if industry_catalog_service is None: 
            raise ValueError( 
                "IndustryCatalogService is required." 
            ) 
 
        if not isinstance( 
            industry_catalog_service, 
            IndustryCatalogService, 
        ): 
            raise TypeError( 
                "industry_catalog_service must be an " 
                "IndustryCatalogService instance." 
            ) 
 
        if parser is None: 
            raise ValueError( 
                "PlanningParser is required." 
            ) 
 
        if planner is None: 
            raise ValueError( 
                "Planner is required." 
            ) 
 
        if execution_engine is None: 
            raise ValueError( 
                "ExecutionEngine is required." 
            ) 
 
        if services is None: 
            raise ValueError( 
                "AgentServices is required." 
            ) 
 
        if not isinstance( 
            services, 
            AgentServices, 
        ): 
            raise TypeError( 
                "services must be an AgentServices instance." 
            ) 
 
        self.db = db 
        self.company_repository = company_repository 
        self.industry_catalog_service = ( 
            industry_catalog_service 
        ) 
 
        self.repository = ResearchRepository(db) 
        self.result_repository = ResearchResultRepository(db) 
 
        self.parser = parser 
        self.planner = planner 
        self.execution_engine = execution_engine 
        self.services = services 
 
        logger.debug( 
            "ResearchService initialized | " 
            "company_repository_id=%s | " 
            "industry_catalog_service_id=%s | " 
            "research_repository_id=%s | " 
            "research_result_repository_id=%s | " 
            "services_id=%s", 
            id(self.company_repository), 
            id(self.industry_catalog_service), 
            id(self.repository), 
            id(self.result_repository), 
            id(self.services), 
        ) 
 
    # ============================================================ 
    # Company Resolution 
    # ============================================================ 
 
    async def _resolve_company( 
        self, 
        *, 
        company_id: int | None, 
        company_name: str | None, 
        ticker: str | None, 
    ) -> dict[str, Any]: 
        """ 
        Resolve exactly one canonical Company record. 
 
        Resolution order: 
 
        1. Explicit company_id. 
        2. CompanyRepository.find_candidates(). 
 
        Canonical values ALWAYS come from Company. 
 
        IMPORTANT: 
        Company.sector is intentionally ignored here. 
        """ 
 
        normalized_company_id = company_id 
 
        if normalized_company_id is not None: 
            try: 
                normalized_company_id = int( 
                    normalized_company_id 
                ) 
            except (TypeError, ValueError) as exc: 
                raise ValueError( 
                    f"Invalid company_id: {company_id!r}" 
                ) from exc 
 
            if normalized_company_id <= 0: 
                raise ValueError( 
                    "company_id must be a positive integer." 
                ) 
 
        company_record: Any | None = None 
 
        # -------------------------------------------------------- 
        # Explicit company ID 
        # -------------------------------------------------------- 
 
        if normalized_company_id is not None: 
 
            company_record = ( 
                await self.company_repository.get_by_id( 
                    normalized_company_id 
                ) 
            ) 
 
            if company_record is None: 
                raise ValueError( 
                    "Company not found: " 
                    f"{normalized_company_id}" 
                ) 
 
        # -------------------------------------------------------- 
        # Name / ticker resolution 
        # -------------------------------------------------------- 
 
        else: 
 
            normalized_company_name = self._clean_string( 
                company_name 
            ) 
 
            normalized_ticker = self._clean_string( 
                ticker 
            ) 
 
            candidate_data: dict[str, Any] = {} 
 
            if normalized_company_name: 
                candidate_data["name"] = ( 
                    normalized_company_name 
                ) 
 
            if normalized_ticker: 
                candidate_data["ticker"] = ( 
                    normalized_ticker 
                ) 
 
            if not candidate_data: 
                raise ValueError( 
                    "company_id or company is required " 
                    "for company research." 
                ) 
 
            logger.info( 
                "Resolving canonical company | " 
                "company=%r | ticker=%r", 
                normalized_company_name, 
                normalized_ticker, 
            ) 
 
            candidates = ( 
                await self.company_repository.find_candidates( 
                    candidate_data 
                ) 
            ) 
 
            if not candidates: 
                raise ValueError( 
                    "Unable to resolve a canonical company " 
                    f"for company={normalized_company_name!r}, " 
                    f"ticker={normalized_ticker!r}. " 
                    "Provide a valid company_id or ensure " 
                    "the company exists in the Company catalog." 
                ) 
 
            company_record = candidates[0] 
 
            candidate_company_id = getattr( 
                company_record, 
                "id", 
                None, 
            ) 
 
            if candidate_company_id is None: 
                raise RuntimeError( 
                    "CompanyRepository returned a company " 
                    "without a database ID." 
                ) 
 
            try: 
                normalized_company_id = int( 
                    candidate_company_id 
                ) 
            except (TypeError, ValueError) as exc: 
                raise RuntimeError( 
                    "CompanyRepository returned an invalid " 
                    f"company ID: {candidate_company_id!r}" 
                ) from exc 
 
            if normalized_company_id <= 0: 
                raise RuntimeError( 
                    "CompanyRepository returned a non-positive " 
                    f"company ID: {normalized_company_id}" 
                ) 
 
        # -------------------------------------------------------- 
        # Canonical Company values 
        # -------------------------------------------------------- 
 
        resolved_company = self._clean_string( 
            getattr( 
                company_record, 
                "name", 
                None, 
            ) 
        ) 
 
        resolved_ticker = self._clean_string( 
            getattr( 
                company_record, 
                "ticker", 
                None, 
            ) 
        ) 
 
        if not resolved_company: 
            raise RuntimeError( 
                "Canonical Company record has no valid name." 
            ) 
 
        if normalized_company_id is None: 
            raise RuntimeError( 
                "Canonical company resolution produced no " 
                "company_id." 
            ) 
 
        logger.info( 
            "Canonical company resolved | " 
            "company_id=%r | company=%r | ticker=%r", 
            normalized_company_id, 
            resolved_company, 
            resolved_ticker, 
        ) 
 
        return { 
            "company_id": normalized_company_id, 
            "company": resolved_company, 
            "ticker": resolved_ticker, 
            "company_record": company_record, 
        } 
 
    # ============================================================ 
    # Industry Resolution 
    # ============================================================ 
 
    async def _resolve_canonical_industry( 
        self, 
        *, 
        company: str, 
        ticker: str | None, 
        company_record: Any | None, 
        research_industry: str | None, 
    ) -> dict[str, Any]: 
        """ 
        Resolve canonical industry. 
 
        Priority: 
 
            Company.industry 
            Company.sub_industry 
            Research/request metadata industry 
            unresolved 
 
        NEVER: 
 
            Company.sector -> industry 
        """ 
 
        company_industry = ( 
            getattr( 
                company_record, 
                "industry", 
                None, 
            ) 
            if company_record is not None 
            else None 
        ) 
 
        company_sub_industry = ( 
            getattr( 
                company_record, 
                "sub_industry", 
                None, 
            ) 
            if company_record is not None 
            else None 
        ) 
 
        company_industry = self._clean_string( 
            company_industry 
        ) 
 
        company_sub_industry = self._clean_string( 
            company_sub_industry 
        ) 
 
        research_industry = self._clean_string( 
            research_industry 
        ) 
 
        # -------------------------------------------------------- 
        # IMPORTANT: 
        # 
        # Company.sector is intentionally NEVER used. 
        # -------------------------------------------------------- 
 
        if company_industry: 
 
            candidate_industry = company_industry 
            candidate_source = "Company.industry" 
 
        elif company_sub_industry: 
 
            candidate_industry = company_sub_industry 
            candidate_source = "Company.sub_industry" 
 
        elif research_industry: 
 
            candidate_industry = research_industry 
            candidate_source = ( 
                "Research.industry / " 
                "request.metadata['industry']" 
            ) 
 
        else: 
 
            candidate_industry = None 
            candidate_source = "unresolved" 
 
        logger.info( 
            "Resolving canonical industry | " 
            "company=%r | ticker=%r | " 
            "candidate=%r | source=%s", 
            company, 
            ticker, 
            candidate_industry, 
            candidate_source, 
        ) 
 
        # -------------------------------------------------------- 
        # Resolve through catalog service. 
        # 
        # The catalog service is allowed to fail gracefully. 
        # A research plan that does not require industry should 
        # still be able to execute. 
        # -------------------------------------------------------- 
 
        try: 
 
            canonical_record = ( 
                await self._call_industry_catalog_resolver( 
                    company=company, 
                    ticker=ticker, 
                    industry=candidate_industry, 
                    company_record=company_record, 
                ) 
            ) 
 
        except Exception as exc: 
 
            logger.warning( 
                "Canonical industry resolution failed | " 
                "company=%r | ticker=%r | " 
                "candidate_industry=%r | " 
                "candidate_source=%s | error=%s", 
                company, 
                ticker, 
                candidate_industry, 
                candidate_source, 
                exc, 
                exc_info=True, 
            ) 
 
            return { 
                "industry": None, 
                "industry_id": None, 
                "industry_source": "unresolved", 
                "industry_record": None, 
            } 
 
        if canonical_record is None: 
 
            logger.warning( 
                "Industry catalog returned no canonical " 
                "industry | company=%r | ticker=%r", 
                company, 
                ticker, 
            ) 
 
            return { 
                "industry": None, 
                "industry_id": None, 
                "industry_source": "unresolved", 
                "industry_record": None, 
            } 
 
        canonical_industry = self._clean_string( 
            self._extract_industry_name( 
                canonical_record 
            ) 
        ) 
 
        canonical_industry_id = ( 
            self._extract_industry_id( 
                canonical_record 
            ) 
        ) 
 
        if not canonical_industry: 
 
            logger.warning( 
                "Industry catalog returned a record without " 
                "a canonical industry name | " 
                "company=%r | ticker=%r", 
                company, 
                ticker, 
            ) 
 
            return { 
                "industry": None, 
                "industry_id": canonical_industry_id, 
                "industry_source": "unresolved", 
                "industry_record": canonical_record, 
            } 
 
        industry_source = ( 
            f"IndustryCatalogService({candidate_source})" 
            if candidate_industry 
            else "IndustryCatalogService" 
        ) 
 
        logger.info( 
            "Canonical industry resolved | " 
            "company=%r | ticker=%r | " 
            "industry=%r | industry_id=%r | source=%s", 
            company, 
            ticker, 
            canonical_industry, 
            canonical_industry_id, 
            industry_source, 
        ) 
 
        return { 
            "industry": canonical_industry, 
            "industry_id": canonical_industry_id, 
            "industry_source": industry_source, 
            "industry_record": canonical_record, 
        } 
 
    async def _call_industry_catalog_resolver( 
        self, 
        *, 
        company: str, 
        ticker: str | None, 
        industry: str | None, 
        company_record: Any | None, 
    ) -> Any: 
        """ 
        Call IndustryCatalogService.resolve() defensively. 
 
        This protects ResearchService from older/newer versions 
        of IndustryCatalogService whose resolve() signatures may 
        differ. 
 
        Preferred signature: 
 
            resolve( 
                company=..., 
                ticker=..., 
                industry=..., 
                company_record=..., 
            ) 
 
        Fallback signatures are attempted only when Python raises 
        TypeError because of unsupported keyword arguments. 
 
        This does NOT map Company.sector to industry. 
        """ 
 
        resolver = getattr( 
            self.industry_catalog_service, 
            "resolve", 
            None, 
        ) 
 
        if not callable(resolver): 
            raise RuntimeError( 
                "IndustryCatalogService does not expose " 
                "a callable resolve() method." 
            ) 
 
        preferred_kwargs = { 
            "company": company, 
            "ticker": ticker, 
            "industry": industry, 
            "company_record": company_record, 
        } 
 
        try: 
            return await resolver( 
                **preferred_kwargs 
            ) 
 
        except TypeError as exc: 
 
            error_text = str(exc).lower() 
 
            unsupported_company_record = ( 
                "company_record" in error_text 
                and ( 
                    "unexpected keyword" in error_text 
                    or "invalid keyword" in error_text 
                    or "got an unexpected keyword" in error_text 
                ) 
            ) 
 
            if unsupported_company_record: 
 
                logger.debug( 
                    "Retrying IndustryCatalogService.resolve " 
                    "without company_record." 
                ) 
 
                return await resolver( 
                    company=company, 
                    ticker=ticker, 
                    industry=industry, 
                ) 
 
            raise 
 
    # ============================================================ 
    # Industry Helpers 
    # ============================================================ 
 
    @staticmethod 
    def _extract_industry_name( 
        industry_record: Any, 
    ) -> str | None: 
 
        if industry_record is None: 
            return None 
 
        if isinstance( 
            industry_record, 
            dict, 
        ): 
 
            value = ( 
                industry_record.get("industry") 
                or industry_record.get("industry_name") 
                or industry_record.get("name") 
            ) 
 
            return ( 
                str(value).strip() 
                if value is not None 
                else None 
            ) 
 
        value = ( 
            getattr( 
                industry_record, 
                "industry", 
                None, 
            ) 
            or getattr( 
                industry_record, 
                "industry_name", 
                None, 
            ) 
            or getattr( 
                industry_record, 
                "name", 
                None, 
            ) 
        ) 
 
        return ( 
            str(value).strip() 
            if value is not None 
            else None 
        ) 
 
    @staticmethod 
    def _extract_industry_id( 
        industry_record: Any, 
    ) -> int | None: 
 
        if industry_record is None: 
            return None 
 
        if isinstance( 
            industry_record, 
            dict, 
        ): 
 
            value = ( 
                industry_record.get("id") 
                or industry_record.get("industry_id") 
            ) 
 
        else: 
 
            value = ( 
                getattr( 
                    industry_record, 
                    "id", 
                    None, 
                ) 
                or getattr( 
                    industry_record, 
                    "industry_id", 
                    None, 
                ) 
            ) 
 
        if value is None: 
            return None 
 
        try: 
            return int(value) 
        except (TypeError, ValueError): 
            return None 
 
    # ============================================================ 
    # Start Research 
    # ============================================================ 
 
    async def start_research( 
        self, 
        request: ResearchStartRequest, 
    ) -> tuple[ 
        ResearchStartResponse, 
        ExecutionPlan, 
    ]: 
 
        if request is None: 
            raise ValueError( 
                "ResearchStartRequest is required." 
            ) 
 
        planning_request = self.parser.parse( 
            request.query 
        ) 
 
        if planning_request is None: 
            raise RuntimeError( 
                "PlanningParser returned no planning request." 
            ) 
 
        execution_plan = self.planner.create_plan( 
            planning_request 
        ) 
 
        if execution_plan is None: 
            raise RuntimeError( 
                "Planner returned no execution plan." 
            ) 
 
        industry_required = self._requires_industry( 
            execution_plan 
        ) 
 
        execution_plan_id = str( 
            execution_plan.id 
        ) 
 
        intent = str( 
            planning_request.intent 
        ) 
 
        research_type = ( 
            request.research_type 
            if request.research_type 
            else intent 
        ) 
 
        company_name = self._clean_string( 
            request.company 
        ) 
 
        ticker = self._clean_string( 
            request.ticker 
        ) 
 
        company_id = request.company_id 
 
        request_metadata: dict[str, Any] = ( 
            self._to_json_safe( 
                request.metadata or {} 
            ) 
        ) 
 
        if not isinstance( 
            request_metadata, 
            dict, 
        ): 
            request_metadata = {} 
 
        research_industry = self._clean_string( 
            request_metadata.get("industry") 
        ) 
 
        # -------------------------------------------------------- 
        # Normalize company ID 
        # -------------------------------------------------------- 
 
        if company_id is not None: 
 
            try: 
                company_id = int(company_id) 
            except (TypeError, ValueError) as exc: 
                raise ValueError( 
                    f"Invalid company_id: {company_id!r}" 
                ) from exc 
 
            if company_id <= 0: 
                raise ValueError( 
                    "company_id must be a positive integer." 
                ) 
 
        if company_id is None and not company_name: 
            raise ValueError( 
                "company_id or company is required " 
                "for company research." 
            ) 
 
        # -------------------------------------------------------- 
        # Resolve canonical company 
        # -------------------------------------------------------- 
 
        resolved_company = ( 
            await self._resolve_company( 
                company_id=company_id, 
                company_name=company_name, 
                ticker=ticker, 
            ) 
        ) 
 
        company_id = resolved_company[ 
            "company_id" 
        ] 
 
        company_name = resolved_company[ 
            "company" 
        ] 
 
        ticker = resolved_company[ 
            "ticker" 
        ] 
 
        company_record = resolved_company[ 
            "company_record" 
        ] 
 
        # -------------------------------------------------------- 
        # Resolve canonical industry 
        # -------------------------------------------------------- 
 
        resolved_industry = ( 
            await self._resolve_canonical_industry( 
                company=company_name, 
                ticker=ticker, 
                company_record=company_record, 
                research_industry=research_industry, 
            ) 
        ) 
 
        industry = resolved_industry[ 
            "industry" 
        ] 
 
        industry_id = resolved_industry[ 
            "industry_id" 
        ] 
 
        industry_source = resolved_industry[ 
            "industry_source" 
        ] 
 
        if industry_required and not industry: 
            raise ValueError( 
                "This research execution plan requires " 
                "a canonical industry, but industry " 
                "resolution was unsuccessful." 
            ) 
 
        # -------------------------------------------------------- 
        # Lifecycle metadata 
        # -------------------------------------------------------- 
 
        research_metadata: dict[str, Any] = { 
            **request_metadata, 
            "company_id": company_id, 
            "company": company_name, 
            "ticker": ticker, 
            "industry": industry, 
            "industry_source": industry_source, 
            "industry_required": industry_required, 
            "progress": 0, 
            "current_stage": "Planning", 
        } 
 
        if industry_id is not None: 
            research_metadata[ 
                "industry_id" 
            ] = industry_id 
 
        research_metadata = self._to_json_safe( 
            research_metadata 
        ) 
 
        if not isinstance( 
            research_metadata, 
            dict, 
        ): 
            research_metadata = {} 
 
        title = ( 
            self._clean_string( 
                request.title 
            ) 
            or company_name 
            or "Research Project" 
        ) 
 
        research = Research( 
            title=title, 
            query=request.query, 
            intent=intent, 
            research_type=research_type, 
            status="queued", 
            company=company_name, 
            ticker=ticker, 
            industry=industry, 
            execution_plan_id=execution_plan_id, 
            metadata_json=research_metadata, 
        ) 
 
        research = await self.repository.create( 
            research 
        ) 
 
        if research.id is None: 
            raise RuntimeError( 
                "Research repository created a Research " 
                "record without a database-generated id." 
            ) 
 
        logger.info( 
            "Research created | " 
            "research_id=%s | " 
            "company_id=%s | " 
            "company=%r | " 
            "ticker=%r | " 
            "industry=%r | " 
            "industry_id=%r", 
            research.id, 
            company_id, 
            company_name, 
            ticker, 
            industry, 
            industry_id, 
        ) 
 
        response = ResearchStartResponse( 
            research=ResearchSummary.model_validate( 
                research 
            ), 
            execution_plan_id=execution_plan_id, 
            message=( 
                "Research project created " 
                "and queued for execution." 
            ), 
        ) 
 
        return response, execution_plan 
 
    # ============================================================ 
    # Execute Research 
    # ============================================================ 
 
    async def execute_research( 
        self, 
        research_id: UUID, 
        execution_plan: ExecutionPlan, 
    ) -> None: 
 
        if research_id is None: 
            raise ValueError( 
                "research_id is required." 
            ) 
 
        if execution_plan is None: 
            raise ValueError( 
                "execution_plan is required." 
            ) 
 
        if not isinstance(research_id, UUID):
            raise ValueError(
                f"Invalid research_id: {research_id!r}"
            )

        normalized_research_id = research_id

        research = await self.repository.get_by_id( 
            normalized_research_id 
        ) 
 
        if research is None: 
            logger.error( 
                "Research project not found | " 
                "research_id=%s", 
                normalized_research_id, 
            ) 
            return 
 
        execution_context: AgentContext | None = None 
 
        try: 
 
            research.status = "running" 
 
            research.started_at = datetime.now( 
                timezone.utc 
            ) 
 
            self._update_progress( 
                research, 
                progress=5, 
                current_stage="Researching", 
            ) 
 
            await self.db.commit() 
 
            if not research.company: 
                raise ValueError( 
                    "Research company is missing." 
                ) 
 
            research_metadata = ( 
                self._safe_metadata( 
                    research.metadata_json 
                ) 
            ) 
 
            company_id = research_metadata.get( 
                "company_id" 
            ) 
 
            if company_id is not None: 
 
                try: 
                    company_id = int( 
                        company_id 
                    ) 
                except (TypeError, ValueError) as exc: 
                    raise ValueError( 
                        "Invalid company_id stored " 
                        "in research metadata." 
                    ) from exc 
 
                if company_id <= 0: 
                    raise ValueError( 
                        "Invalid company_id stored " 
                        "in research metadata." 
                    ) 
 
            research_industry = self._clean_string( 
                research.industry 
                or research_metadata.get( 
                    "industry" 
                ) 
            ) 
 
            # ---------------------------------------------------- 
            # Re-resolve canonical company 
            # ---------------------------------------------------- 
 
            resolved_company = ( 
                await self._resolve_company( 
                    company_id=company_id, 
                    company_name=research.company, 
                    ticker=research.ticker, 
                ) 
            ) 
 
            company_id = resolved_company[ 
                "company_id" 
            ] 
 
            company_name = resolved_company[ 
                "company" 
            ] 
 
            ticker = resolved_company[ 
                "ticker" 
            ] 
 
            company_record = resolved_company[ 
                "company_record" 
            ] 
 
            # ---------------------------------------------------- 
            # Re-resolve canonical industry 
            # ---------------------------------------------------- 
 
            resolved_industry = ( 
                await self._resolve_canonical_industry( 
                    company=company_name, 
                    ticker=ticker, 
                    company_record=company_record, 
                    research_industry=research_industry, 
                ) 
            ) 
 
            industry = resolved_industry[ 
                "industry" 
            ] 
 
            industry_id = resolved_industry[ 
                "industry_id" 
            ] 
 
            industry_source = resolved_industry[ 
                "industry_source" 
            ] 
 
            industry_required = self._requires_industry( 
                execution_plan 
            ) 
 
            if industry_required and not industry: 
                raise ValueError( 
                    "Execution plan requires canonical " 
                    "industry information, but industry " 
                    "resolution failed." 
                ) 
 
            # ---------------------------------------------------- 
            # Persist canonical identity 
            # ---------------------------------------------------- 
 
            research.company = company_name 
            research.ticker = ticker 
            research.industry = industry 
 
            research_metadata.update( 
                { 
                    "company_id": company_id, 
                    "company": company_name, 
                    "ticker": ticker, 
                    "industry": industry, 
                    "industry_source": industry_source, 
                    "industry_required": industry_required, 
                } 
            ) 
 
            if industry_id is not None: 
 
                research_metadata[ 
                    "industry_id" 
                ] = industry_id 
 
            else: 
 
                research_metadata.pop( 
                    "industry_id", 
                    None, 
                ) 
 
            research.metadata_json = ( 
                self._to_json_safe( 
                    research_metadata 
                ) 
            ) 
 
            await self.db.flush() 
 
            # ==================================================== 
            # ONE CANONICAL AGENT CONTEXT 
            # ==================================================== 
 
            execution_context = AgentContext( 
                research_id=research.id, 
                query=research.query, 
                user_query=research.query, 
                intent=research.intent, 
                research_type=research.research_type, 
                company_id=company_id, 
                company=company_name, 
                ticker=ticker, 
                industry=industry, 
                services=self.services, 
                company_repository=self.company_repository, 
                metadata={ 
                    **research_metadata, 
                    "company_id": company_id, 
                    "company": company_name, 
                    "ticker": ticker, 
                    "industry": industry, 
                    "industry_source": industry_source, 
                    "industry_required": industry_required, 
                }, 
            ) 
 
            self._validate_agent_context( 
                execution_context, 
                expected_company_id=company_id, 
                expected_company=company_name, 
                expected_ticker=ticker, 
                expected_industry=industry, 
                industry_required=industry_required, 
            ) 
 
            self._log_context_checkpoint( 
                execution_context 
            ) 
 
            self._update_progress( 
                research, 
                progress=10, 
                current_stage="Executing research plan", 
            ) 
 
            await self.db.commit() 
 
            # ==================================================== 
            # EXECUTE 
            # ==================================================== 
 
            execution_result = ( 
                await self.execution_engine.execute( 
                    execution_plan, 
                    context=execution_context, 
                ) 
            ) 
 
            if execution_result is None: 
                raise RuntimeError( 
                    "ExecutionEngine returned no " 
                    "execution result." 
                ) 
 
            execution_success = getattr( 
                execution_result, 
                "success", 
                None, 
            ) 
 
            if execution_success is False: 
                raise RuntimeError( 
                    self._build_execution_failure_message( 
                        research_id=normalized_research_id, 
                        execution_result=execution_result, 
                    ) 
                ) 
 
            if execution_success is None: 
                logger.warning( 
                    "ExecutionEngine result has no explicit " 
                    "success flag | research_id=%s", 
                    normalized_research_id, 
                ) 
 
            # ==================================================== 
            # SERIALIZE 
            # ==================================================== 
 
            self._update_progress( 
                research, 
                progress=90, 
                current_stage="Building research results", 
            ) 
 
            await self.db.flush() 
 
            result_data = ( 
                self._serialize_execution_result( 
                    execution_result 
                ) 
            ) 
 
            # ==================================================== 
            # PERSIST 
            # ==================================================== 
 
            await self._persist_research_result( 
                research=research, 
                result_data=result_data, 
            ) 
 
            # ==================================================== 
            # COMPLETE 
            # ==================================================== 
 
            final_metadata = ( 
                self._safe_metadata( 
                    research.metadata_json 
                ) 
            ) 
 
            final_metadata.update( 
                { 
                    "company_id": company_id, 
                    "company": company_name, 
                    "ticker": ticker, 
                    "industry": industry, 
                    "industry_source": industry_source, 
                    "industry_required": industry_required, 
                    "progress": 100, 
                    "current_stage": "Completed", 
                } 
            ) 
 
            if industry_id is not None: 
                final_metadata[ 
                    "industry_id" 
                ] = industry_id 
 
            research.metadata_json = ( 
                self._to_json_safe( 
                    final_metadata 
                ) 
            ) 
 
            research.status = "completed" 
 
            research.completed_at = datetime.now( 
                timezone.utc 
            ) 
 
            await self.db.commit() 
 
            logger.info( 
                "Research completed successfully | " 
                "research_id=%s | " 
                "context_object_id=%s | " 
                "company_id=%s | " 
                "industry=%r", 
                normalized_research_id, 
                id(execution_context), 
                company_id, 
                industry, 
            ) 
 
        except Exception as exc: 
 
            logger.exception( 
                "Research execution failed | " 
                "research_id=%s", 
                normalized_research_id, 
            ) 
 
            try: 
                await self.db.rollback() 
 
            except Exception: 
                logger.exception( 
                    "Database rollback failed | " 
                    "research_id=%s", 
                    normalized_research_id, 
                ) 
 
            try: 
 
                research = ( 
                    await self.repository.get_by_id( 
                        normalized_research_id 
                    ) 
                ) 
 
                if research is not None: 
 
                    metadata = ( 
                        self._safe_metadata( 
                            research.metadata_json 
                        ) 
                    ) 
 
                    metadata["current_stage"] = "Failed" 
                    metadata["error"] = str(exc) 
 
                    # Preserve the latest known progress. 
                    if "progress" not in metadata: 
                        metadata["progress"] = 0 
 
                    research.status = "failed" 
 
                    research.metadata_json = ( 
                        self._to_json_safe( 
                            metadata 
                        ) 
                    ) 
 
                    await self.db.commit() 
 
            except Exception: 
 
                logger.exception( 
                    "Failed to persist failed status | " 
                    "research_id=%s", 
                    normalized_research_id, 
                ) 
 
            raise 
 
    # ============================================================ 
    # Persist Research Result 
    # ============================================================ 
 
    async def _persist_research_result( 
        self, 
        *, 
        research: Research, 
        result_data: dict[str, Any], 
    ) -> ResearchResult: 
 
        if research.id is None: 
            raise RuntimeError( 
                "Cannot persist ResearchResult without " 
                "a research ID." 
            ) 
 
        if not isinstance( 
            result_data, 
            dict, 
        ): 
            raise ValueError( 
                "Research result data must be a dictionary." 
            ) 
 
        result_data = self._to_json_safe( 
            result_data 
        ) 
 
        if not isinstance( 
            result_data, 
            dict, 
        ): 
            raise ValueError( 
                "Research result normalization produced " 
                "invalid data." 
            ) 
 
        overview = result_data.get( 
            "overview" 
        ) 
 
        if not isinstance( 
            overview, 
            dict, 
        ): 
            overview = {} 
 
        evidence = result_data.get( 
            "evidence" 
        ) 
 
        if not isinstance( 
            evidence, 
            list, 
        ): 
            evidence = [] 
 
        documents = result_data.get( 
            "documents" 
        ) 
 
        if not isinstance( 
            documents, 
            list, 
        ): 
            documents = [] 
 
        insights = result_data.get( 
            "insights" 
        ) 
 
        if not isinstance( 
            insights, 
            list, 
        ): 
            insights = [] 
 
        report = result_data.get( 
            "report" 
        ) 
 
        if not isinstance( 
            report, 
            dict, 
        ): 
            report = {} 
 
        sections = report.get( 
            "sections" 
        ) 
 
        if not isinstance( 
            sections, 
            list, 
        ): 
            sections = [] 
 
        agent_results = result_data.get( 
            "agent_results" 
        ) 
 
        if not isinstance( 
            agent_results, 
            list, 
        ): 
            agent_results = [] 
 
        citations = result_data.get( 
            "citations" 
        ) 
 
        if not isinstance( 
            citations, 
            list, 
        ): 
            citations = [] 
 
        summary = report.get( 
            "summary" 
        ) 
 
        if summary is not None: 
            summary = str(summary) 
 
        payload = { 
            "summary": summary, 
            "overview": self._to_json_safe( 
                overview 
            ), 
            "evidence": self._to_json_safe( 
                evidence 
            ), 
            "documents": self._to_json_safe( 
                documents 
            ), 
            "insights": self._to_json_safe( 
                insights 
            ), 
            "sections": self._to_json_safe( 
                sections 
            ), 
            "agent_results": self._to_json_safe( 
                agent_results 
            ), 
            "citations": self._to_json_safe( 
                citations 
            ), 
        } 
 
        existing = ( 
            await self.result_repository.get_by_research_id( 
                research.id 
            ) 
        ) 
 
        if existing is None: 
 
            research_result = ResearchResult( 
                research_id=research.id, 
                **payload, 
            ) 
 
            saved_result = ( 
                await self.result_repository.create( 
                    research_result 
                ) 
            ) 
 
        else: 
 
            existing.summary = payload[ 
                "summary" 
            ] 
 
            existing.overview = payload[ 
                "overview" 
            ] 
 
            existing.evidence = payload[ 
                "evidence" 
            ] 
 
            existing.documents = payload[ 
                "documents" 
            ] 
 
            existing.insights = payload[ 
                "insights" 
            ] 
 
            existing.sections = payload[ 
                "sections" 
            ] 
 
            existing.agent_results = payload[ 
                "agent_results" 
            ] 
 
            existing.citations = payload[ 
                "citations" 
            ] 
 
            saved_result = ( 
                await self.result_repository.update( 
                    existing 
                ) 
            ) 
 
        logger.info( 
            "ResearchResult persisted | " 
            "research_id=%s | result_id=%s | " 
            "overview=%s | evidence=%s | " 
            "documents=%s | insights=%s | " 
            "sections=%s | agent_results=%s | " 
            "citations=%s", 
            research.id, 
            saved_result.id, 
            bool(overview), 
            len(evidence), 
            len(documents), 
            len(insights), 
            len(sections), 
            len(agent_results), 
            len(citations), 
        ) 
 
        return saved_result 
 
    # ============================================================ 
    # Execution Plan Inspection 
    # ============================================================ 
 
    @staticmethod 
    def _requires_industry( 
        execution_plan: ExecutionPlan, 
    ) -> bool: 
 
        if execution_plan is None: 
            return False 
 
        def as_data(value: Any) -> Any: 
 
            if value is None: 
                return None 
 
            if isinstance( 
                value, 
                dict, 
            ): 
                return value 
 
            for method_name in ( 
                "model_dump", 
                "dict", 
                "to_dict", 
            ): 
 
                method = getattr( 
                    value, 
                    method_name, 
                    None, 
                ) 
 
                if callable(method): 
 
                    try: 
 
                        result = method() 
 
                        if isinstance( 
                            result, 
                            dict, 
                        ): 
                            return result 
 
                    except Exception: 
                        pass 
 
            if is_dataclass(value): 
 
                try: 
                    return as_data( 
                        asdict(value) 
                    ) 
                except Exception: 
                    pass 
 
            if hasattr( 
                value, 
                "__dict__", 
            ): 
 
                try: 
                    return vars(value) 
                except Exception: 
                    pass 
 
            return value 
 
        def contains_industry( 
            value: Any, 
        ) -> bool: 
 
            value = as_data(value) 
 
            if isinstance( 
                value, 
                dict, 
            ): 
 
                for key, child in value.items(): 
 
                    normalized_key = ( 
                        str(key) 
                        .strip() 
                        .lower() 
                        .replace("-", "_") 
                    ) 
 
                    if normalized_key in { 
                        "agent", 
                        "agent_name", 
                        "agent_id", 
                        "task_type", 
                        "task_name", 
                        "name", 
                        "type", 
                        "capability", 
                    }: 
 
                        if isinstance( 
                            child, 
                            str, 
                        ): 
 
                            normalized = ( 
                                child 
                                .strip() 
                                .lower() 
                                .replace("-", "_") 
                                .replace(" ", "_") 
                            ) 
 
                            if normalized in { 
                                "industry", 
                                "industry_agent", 
                                "industryagent", 
                                "industry_task", 
                                "industry_analysis", 
                            }: 
                                return True 
 
                            if ( 
                                "industry" 
                                in normalized 
                                and "agent" 
                                in normalized 
                            ): 
                                return True 
 
                    if contains_industry( 
                        child 
                    ): 
                        return True 
 
                return False 
 
            if isinstance( 
                value, 
                ( 
                    list, 
                    tuple, 
                    set, 
                ), 
            ): 
 
                return any( 
                    contains_industry(item) 
                    for item in value 
                ) 
 
            return False 
 
        return contains_industry( 
            execution_plan 
        ) 
 
    # ============================================================ 
    # Agent Context Validation 
    # ============================================================ 
 
    @staticmethod 
    def _validate_agent_context( 
        context: AgentContext, 
        *, 
        expected_company_id: int | None, 
        expected_company: str, 
        expected_ticker: str | None, 
        expected_industry: str | None, 
        industry_required: bool = False, 
    ) -> None: 
 
        if context is None: 
            raise RuntimeError( 
                "AgentContext was not created." 
            ) 
 
        if context.services is None: 
            raise RuntimeError( 
                "AgentContext.services is required." 
            ) 
 
        if context.company_repository is None: 
            raise RuntimeError( 
                "AgentContext.company_repository " 
                "is required." 
            ) 
 
        if expected_company_id is None: 
            raise RuntimeError( 
                "Canonical company_id is required " 
                "for AgentContext." 
            ) 
 
        if context.company_id != expected_company_id: 
            raise RuntimeError( 
                "AgentContext company_id propagation failed." 
            ) 
 
        if context.company != expected_company: 
            raise RuntimeError( 
                "AgentContext company propagation failed." 
            ) 
 
        if context.ticker != expected_ticker: 
            raise RuntimeError( 
                "AgentContext ticker propagation failed." 
            ) 
 
        if context.industry != expected_industry: 
            raise RuntimeError( 
                "AgentContext industry propagation failed." 
            ) 
 
        if not context.company: 
            raise RuntimeError( 
                "AgentContext.company is required." 
            ) 
 
        if ( 
            industry_required 
            and not context.industry 
        ): 
            raise RuntimeError( 
                "AgentContext.industry is required " 
                "for this execution plan." 
            ) 
 
        metadata = ( 
            context.metadata 
            or {} 
        ) 
 
        checks = ( 
            ( 
                "company_id", 
                context.company_id, 
            ), 
            ( 
                "company", 
                context.company, 
            ), 
            ( 
                "ticker", 
                context.ticker, 
            ), 
            ( 
                "industry", 
                context.industry, 
            ), 
        ) 
 
        for key, context_value in checks: 
 
            metadata_value = metadata.get( 
                key 
            ) 
 
            if ( 
                context_value is not None 
                and metadata_value is not None 
                and str(context_value) 
                != str(metadata_value) 
            ): 
 
                raise RuntimeError( 
                    f"AgentContext {key} mismatch." 
                ) 
 
    # ============================================================ 
    # Execution Failure 
    # ============================================================ 
 
    @staticmethod 
    def _build_execution_failure_message( 
        *, 
        research_id: UUID, 
        execution_result: Any, 
    ) -> str: 
 
        metadata = getattr( 
            execution_result, 
            "metadata", 
            None, 
        ) 
 
        if not isinstance( 
            metadata, 
            dict, 
        ): 
            metadata = {} 
 
        failed_tasks = metadata.get( 
            "failed_tasks", 
            0, 
        ) 
 
        completed_tasks = metadata.get( 
            "completed_tasks", 
            0, 
        ) 
 
        total_tasks = metadata.get( 
            "total_tasks", 
            0, 
        ) 
 
        failures = metadata.get( 
            "failures", 
            [], 
        ) 
 
        if not isinstance( 
            failures, 
            ( 
                list, 
                tuple, 
            ), 
        ): 
            failures = [] 
 
        details: list[str] = [] 
 
        for failure in failures: 
 
            if not isinstance( 
                failure, 
                dict, 
            ): 
                continue 
 
            task_id = failure.get( 
                "task_id", 
                "unknown", 
            ) 
 
            error = failure.get( 
                "error", 
                "unknown error", 
            ) 
 
            details.append( 
                f"task={task_id}: {error}" 
            ) 
 
        message = ( 
            "Research execution failed: " 
            f"{failed_tasks} task(s) failed, " 
            f"{completed_tasks}/{total_tasks} " 
            "task(s) completed." 
        ) 
 
        if details: 
            message += ( 
                " Failures: " 
                + "; ".join(details) 
            ) 
 
        return message 
 
    # ============================================================ 
    # Context Logging 
    # ============================================================ 
 
    @staticmethod 
    def _log_context_checkpoint( 
        context: AgentContext, 
    ) -> None: 
 
        logger.info( 
            "CANONICAL AGENT CONTEXT CREATED | " 
            "context_object_id=%s | " 
            "services_object_id=%s | " 
            "company_repository_object_id=%s | " 
            "research_id=%r | " 
            "company_id=%r | " 
            "company=%r | " 
            "ticker=%r | " 
            "industry=%r", 
            id(context), 
            ( 
                id(context.services) 
                if context.services is not None 
                else None 
            ), 
            ( 
                id(context.company_repository) 
                if context.company_repository is not None 
                else None 
            ), 
            context.research_id, 
            context.company_id, 
            context.company, 
            context.ticker, 
            context.industry, 
        ) 
 
    # ============================================================ 
    # Progress 
    # ============================================================ 
 
    # ============================================================
    # Progress
    # ============================================================

    def _update_progress(
        self,
        research: Research,
        *,
        progress: int,
        current_stage: str,
    ) -> None:
        """
        Update research lifecycle progress metadata safely.

        research.metadata_json stores lifecycle/context metadata only.
        Canonical completed research output belongs in ResearchResult.

        Progress is always normalized to the inclusive range 0..100.
        """

        if research is None:
            raise ValueError(
                "Research is required when updating progress."
            )

        metadata = self._safe_metadata(
            research.metadata_json
        )

        try:
            normalized_progress = int(progress)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid research progress value; "
                "defaulting to 0 | "
                "research_id=%r | progress=%r",
                getattr(research, "id", None),
                progress,
            )
            normalized_progress = 0

        normalized_progress = max(
            0,
            min(
                normalized_progress,
                100,
            ),
        )

        normalized_stage = (
            self._clean_string(current_stage)
            or "Unknown"
        )

        metadata["progress"] = normalized_progress
        metadata["current_stage"] = normalized_stage

        research.metadata_json = self._to_json_safe(
            metadata
        )

        logger.debug(
            "Research progress updated | "
            "research_id=%r | "
            "progress=%s | "
            "current_stage=%r",
            getattr(research, "id", None),
            normalized_progress,
            normalized_stage,
        )
    # ============================================================ 
    # Serialization 
    # ============================================================ 
 
    def _serialize_execution_result( 
        self, 
        execution_result: Any, 
    ) -> dict[str, Any]: 
 
        raw = self._to_json_safe( 
            execution_result 
        ) 
 
        if not isinstance( 
            raw, 
            dict, 
        ): 
            raw = { 
                "result": raw 
            } 
 
        metadata = raw.get( 
            "metadata" 
        ) 
 
        if not isinstance( 
            metadata, 
            dict, 
        ): 
            metadata = {} 
 
        task_results = ( 
            raw.get("task_results") 
            or raw.get("results") 
            or metadata.get("task_results") 
            or metadata.get("results") 
            or {} 
        ) 
 
        agent_results: list[ 
            dict[str, Any] 
        ] = [] 
 
        # ======================================================== 
        # Normalize task results 
        # ======================================================== 
 
        if isinstance( 
            task_results, 
            dict, 
        ): 
 
            for task_id, task_result in ( 
                task_results.items() 
            ): 
 
                normalized = self._to_json_safe( 
                    task_result 
                ) 
 
                if isinstance( 
                    normalized, 
                    dict, 
                ): 
 
                    normalized.setdefault( 
                        "task_id", 
                        str(task_id), 
                    ) 
 
                    agent_results.append( 
                        normalized 
                    ) 
 
                else: 
 
                    agent_results.append( 
                        { 
                            "task_id": str( 
                                task_id 
                            ), 
                            "result": normalized, 
                        } 
                    ) 
 
        elif isinstance( 
            task_results, 
            list, 
        ): 
 
            for index, task_result in enumerate( 
                task_results 
            ): 
 
                normalized = self._to_json_safe( 
                    task_result 
                ) 
 
                if isinstance( 
                    normalized, 
                    dict, 
                ): 
 
                    normalized.setdefault( 
                        "task_id", 
                        str(index), 
                    ) 
 
                    agent_results.append( 
                        normalized 
                    ) 
 
                else: 
 
                    agent_results.append( 
                        { 
                            "task_id": str(index), 
                            "result": normalized, 
                        } 
                    ) 
 
        # ======================================================== 
        # Helpers 
        # ======================================================== 
 
        def first_dict( 
            *values: Any, 
        ) -> dict[str, Any]: 
 
            for value in values: 
 
                if ( 
                    isinstance(value, dict) 
                    and value 
                ): 
                    return value 
 
            return {} 
 
        def first_list( 
            *values: Any, 
        ) -> list[Any]: 
 
            for value in values: 
 
                if ( 
                    isinstance(value, list) 
                    and value 
                ): 
                    return value 
 
            return [] 
 
        def first_string( 
            *values: Any, 
        ) -> str | None: 
 
            for value in values: 
 
                if value is None: 
                    continue 
 
                if isinstance( 
                    value, 
                    str, 
                ): 
 
                    cleaned = value.strip() 
 
                    if cleaned: 
                        return cleaned 
 
            return None 
 
        # ======================================================== 
        # Existing top-level structured result 
        # ======================================================== 
 
        overview = first_dict( 
            metadata.get("overview"), 
            raw.get("overview"), 
        ) 
 
        evidence = first_list( 
            metadata.get("evidence"), 
            raw.get("evidence"), 
        ) 
 
        documents = first_list( 
            metadata.get("documents"), 
            raw.get("documents"), 
        ) 
 
        insights = first_list( 
            metadata.get("insights"), 
            raw.get("insights"), 
        ) 
 
        raw_report = first_dict( 
            metadata.get("report"), 
            raw.get("report"), 
        ) 
 
        # ======================================================== 
        # Extract structured information from agents 
        # ======================================================== 
 
        company_profile: dict[str, Any] = {} 
        business_model: dict[str, Any] = {} 
        financials: dict[str, Any] = {} 
        investment_view: dict[str, Any] = {} 
 
        extracted_insights: list[Any] = [] 
        extracted_evidence: list[Any] = [] 
        extracted_documents: list[Any] = [] 
 
        agent_summaries: list[str] = [] 
 
        report_sections: list[ 
            dict[str, Any] 
        ] = [] 
 
        for agent_result in agent_results: 
 
            if not isinstance( 
                agent_result, 
                dict, 
            ): 
                continue 
 
            payload = first_dict( 
                agent_result.get("output"), 
                agent_result.get("result"), 
                agent_result.get("data"), 
                agent_result.get("response"), 
            ) 
 
            if not payload: 
                payload = agent_result 
 
            deterministic = first_dict( 
                payload.get( 
                    "deterministic_analysis" 
                ), 
                payload.get( 
                    "analysis" 
                ), 
            ) 
 
            profile = first_dict( 
                payload.get( 
                    "company_profile" 
                ), 
                payload.get( 
                    "profile" 
                ), 
                deterministic.get( 
                    "profile" 
                ), 
            ) 
 
            if profile: 
                company_profile.update( 
                    profile 
                ) 
 
            model = first_dict( 
                payload.get( 
                    "business_model" 
                ), 
                deterministic.get( 
                    "business_model" 
                ), 
            ) 
 
            if model: 
                business_model.update( 
                    model 
                ) 
 
            financial_data = first_dict( 
                payload.get( 
                    "financials" 
                ), 
                payload.get( 
                    "financial_analysis" 
                ), 
                payload.get( 
                    "financial_data" 
                ), 
                deterministic.get( 
                    "financials" 
                ), 
            ) 
 
            if financial_data: 
                financials.update( 
                    financial_data 
                ) 
 
            committee = first_dict( 
                payload.get( 
                    "investment_committee" 
                ), 
                payload.get( 
                    "investment_view" 
                ), 
                payload.get( 
                    "investment_analysis" 
                ), 
            ) 
 
            if committee: 
                investment_view.update( 
                    committee 
                ) 
 
            summary = first_string( 
                payload.get("summary"), 
                payload.get( 
                    "executive_summary" 
                ), 
                payload.get( 
                    "conclusion" 
                ), 
                payload.get( 
                    "thesis" 
                ), 
            ) 
 
            if summary: 
                agent_summaries.append( 
                    summary 
                ) 
 
            # ---------------------------------------------------- 
            # Evidence 
            # ---------------------------------------------------- 
 
            agent_evidence = first_list( 
                payload.get("evidence"), 
                payload.get("sources"), 
                payload.get("citations"), 
            ) 
 
            if agent_evidence: 
                extracted_evidence.extend( 
                    agent_evidence 
                ) 
 
            # ---------------------------------------------------- 
            # Documents 
            # ---------------------------------------------------- 
 
            agent_documents = first_list( 
                payload.get("documents"), 
                payload.get( 
                    "sources_documents" 
                ), 
                payload.get( 
                    "source_documents" 
                ), 
            ) 
 
            if agent_documents: 
                extracted_documents.extend( 
                    agent_documents 
                ) 
 
            # ---------------------------------------------------- 
            # Insights 
            # ---------------------------------------------------- 
 
            agent_insights = first_list( 
                payload.get("insights"), 
                payload.get( 
                    "key_insights" 
                ), 
                payload.get( 
                    "findings" 
                ), 
                payload.get( 
                    "key_findings" 
                ), 
            ) 
 
            if agent_insights: 
                extracted_insights.extend( 
                    agent_insights 
                ) 
 
            # ---------------------------------------------------- 
            # Agent-level report 
            # ---------------------------------------------------- 
 
            agent_report = first_dict( 
                payload.get("report"), 
                payload.get( 
                    "research_report" 
                ), 
            ) 
 
            if agent_report: 
 
                if not raw_report: 
                    raw_report = {} 
 
                if ( 
                    not raw_report.get( 
                        "title" 
                    ) 
                    and agent_report.get( 
                        "title" 
                    ) 
                ): 
                    raw_report["title"] = ( 
                        agent_report["title"] 
                    ) 
 
                if ( 
                    not raw_report.get( 
                        "summary" 
                    ) 
                    and agent_report.get( 
                        "summary" 
                    ) 
                ): 
                    raw_report["summary"] = ( 
                        agent_report["summary"] 
                    ) 
 
                agent_report_sections = ( 
                    agent_report.get( 
                        "sections" 
                    ) 
                ) 
 
                if isinstance( 
                    agent_report_sections, 
                    list, 
                ): 
                    report_sections.extend( 
                        agent_report_sections 
                    ) 
 
        # ======================================================== 
        # Build overview 
        # ======================================================== 
 
        if not overview: 
 
            profile = { 
                "name": first_string( 
                    company_profile.get( 
                        "company_name" 
                    ), 
                    company_profile.get( 
                        "name" 
                    ), 
                    metadata.get( 
                        "company" 
                    ), 
                    raw.get( 
                        "company" 
                    ), 
                ), 
                "ticker": first_string( 
                    company_profile.get( 
                        "ticker" 
                    ), 
                    metadata.get( 
                        "ticker" 
                    ), 
                    raw.get( 
                        "ticker" 
                    ), 
                ), 
                "description": first_string( 
                    company_profile.get( 
                        "description" 
                    ), 
                    company_profile.get( 
                        "business_description" 
                    ), 
                ), 
                "sector": first_string( 
                    company_profile.get( 
                        "sector" 
                    ) 
                ), 
                "industry": first_string( 
                    company_profile.get( 
                        "industry" 
                    ), 
                    metadata.get( 
                        "industry" 
                    ), 
                    raw.get( 
                        "industry" 
                    ), 
                ), 
                "employees": company_profile.get( 
                    "employees" 
                ), 
                "founded": company_profile.get( 
                    "founded" 
                ), 
            } 
 
            profile = { 
                key: value 
                for key, value in profile.items() 
                if value is not None 
            } 
 
            overview = { 
                "profile": profile, 
                "market": {}, 
                "financials": financials, 
            } 
 
            if business_model: 
                overview[ 
                    "business_model" 
                ] = business_model 
 
        else: 
 
            if not isinstance( 
                overview.get("profile"), 
                dict, 
            ): 
                overview["profile"] = {} 
 
            if company_profile: 
                overview[ 
                    "profile" 
                ].update( 
                    company_profile 
                ) 
 
            if financials: 
 
                existing_financials = ( 
                    overview.get( 
                        "financials" 
                    ) 
                ) 
 
                if not isinstance( 
                    existing_financials, 
                    dict, 
                ): 
                    existing_financials = {} 
 
                existing_financials.update( 
                    financials 
                ) 
 
                overview[ 
                    "financials" 
                ] = existing_financials 
 
            if business_model: 
                overview[ 
                    "business_model" 
                ] = business_model 
 
        # ======================================================== 
        # Ensure canonical identity is present in overview 
        # ======================================================== 
 
        overview_profile = overview.get( 
            "profile" 
        ) 
 
        if not isinstance( 
            overview_profile, 
            dict, 
        ): 
            overview_profile = {} 
 
        if metadata.get("company"): 
            overview_profile[ 
                "name" 
            ] = metadata["company"] 
 
        if metadata.get("ticker"): 
            overview_profile[ 
                "ticker" 
            ] = metadata["ticker"] 
 
        if metadata.get("industry"): 
            overview_profile[ 
                "industry" 
            ] = metadata["industry"] 
 
        overview[ 
            "profile" 
        ] = overview_profile 
 
        # ======================================================== 
        # Fill missing collections 
        # ======================================================== 
 
        if not evidence: 
            evidence = extracted_evidence 
 
        if not documents: 
            documents = extracted_documents 
 
        if not insights: 
            insights = extracted_insights 
 
        # ======================================================== 
        # Summary 
        # ======================================================== 
 
        summary = first_string( 
            raw_report.get("summary"), 
            metadata.get("summary"), 
            raw.get("summary"), 
            *agent_summaries, 
        ) 
 
        if not summary and investment_view: 
 
            summary = first_string( 
                investment_view.get( 
                    "summary" 
                ), 
                investment_view.get( 
                    "thesis" 
                ), 
                investment_view.get( 
                    "decision" 
                ), 
                investment_view.get( 
                    "reasoning" 
                ), 
            ) 
 
        # ======================================================== 
        # Report sections 
        # ======================================================== 
 
        raw_sections = raw_report.get( 
            "sections" 
        ) 
 
        if isinstance( 
            raw_sections, 
            list, 
        ): 
            report_sections = ( 
                raw_sections 
                + report_sections 
            ) 
 
        elif isinstance( 
            raw_sections, 
            dict, 
        ): 
 
            for section_id, section_value in ( 
                raw_sections.items() 
            ): 
 
                if isinstance( 
                    section_value, 
                    dict, 
                ): 
 
                    report_sections.append( 
                        { 
                            **section_value, 
                            "id": str( 
                                section_value.get( 
                                    "id", 
                                    section_id, 
                                ) 
                            ), 
                            "title": str( 
                                section_value.get( 
                                    "title", 
                                    section_id, 
                                ) 
                            ), 
                        } 
                    ) 
 
                else: 
 
                    report_sections.append( 
                        { 
                            "id": str( 
                                section_id 
                            ), 
                            "title": str( 
                                section_id 
                            ), 
                            "content": section_value, 
                            "status": "complete", 
                        } 
                    ) 
 
        if not report_sections: 
 
            if company_profile: 
                report_sections.append( 
                    { 
                        "id": "company-profile", 
                        "title": "Company Profile", 
                        "content": company_profile, 
                        "status": "complete", 
                    } 
                ) 
 
            if business_model: 
                report_sections.append( 
                    { 
                        "id": "business-model", 
                        "title": "Business Model", 
                        "content": business_model, 
                        "status": "complete", 
                    } 
                ) 
 
            if financials: 
                report_sections.append( 
                    { 
                        "id": "financial-analysis", 
                        "title": "Financial Analysis", 
                        "content": financials, 
                        "status": "complete", 
                    } 
                ) 
 
            if investment_view: 
                report_sections.append( 
                    { 
                        "id": "investment-view", 
                        "title": "Investment View", 
                        "content": investment_view, 
                        "status": "complete", 
                    } 
                ) 
 
        raw_report = { 
            **raw_report, 
            "summary": summary or "", 
            "sections": report_sections, 
        } 
 
        report = self._normalize_report( 
            raw_report=raw_report, 
            metadata=metadata, 
            raw=raw, 
        ) 
 
        # ======================================================== 
        # Citations 
        # ======================================================== 
 
        citations = first_list( 
            metadata.get( 
                "citations" 
            ), 
            raw.get( 
                "citations" 
            ), 
        ) 
 
        if not citations: 
            citations = extracted_evidence 
 
        return self._to_json_safe( 
            { 
                "overview": overview, 
                "evidence": evidence, 
                "documents": documents, 
                "insights": insights, 
                "report": report, 
                "agent_results": agent_results, 
                "citations": citations, 
                "execution": { 
                    "success": raw.get( 
                        "success", 
                        True, 
                    ), 
                    "metadata": metadata, 
                    "task_results": task_results, 
                }, 
            } 
        ) 
 
    # ============================================================ 
    # Report Normalization 
    # ============================================================ 
 
    def _normalize_report( 
        self, 
        *, 
        raw_report: Any, 
        metadata: dict[str, Any], 
        raw: dict[str, Any], 
    ) -> dict[str, Any]: 
 
        report_title = ( 
            metadata.get( 
                "report_title" 
            ) 
            or raw.get( 
                "report_title" 
            ) 
            or metadata.get( 
                "title" 
            ) 
            or raw.get( 
                "title" 
            ) 
        ) 
 
        report_summary = ( 
            metadata.get( 
                "summary" 
            ) 
            or raw.get( 
                "summary" 
            ) 
            or "" 
        ) 
 
        sections_source = ( 
            metadata.get( 
                "sections" 
            ) 
            or raw.get( 
                "sections" 
            ) 
            or [] 
        ) 
 
        if isinstance( 
            raw_report, 
            dict, 
        ): 
 
            report_title = ( 
                raw_report.get( 
                    "title" 
                ) 
                or report_title 
            ) 
 
            report_summary = ( 
                raw_report.get( 
                    "summary" 
                ) 
                or report_summary 
            ) 
 
            sections_source = ( 
                raw_report.get( 
                    "sections" 
                ) 
                or sections_source 
            ) 
 
        elif isinstance( 
            raw_report, 
            str, 
        ): 
 
            if raw_report.strip(): 
 
                if not report_summary: 
                    report_summary = ( 
                        raw_report.strip() 
                    ) 
 
                if not sections_source: 
                    sections_source = [ 
                        { 
                            "id": "report", 
                            "title": "Research Report", 
                            "content": ( 
                                raw_report.strip() 
                            ), 
                            "status": "complete", 
                        } 
                    ] 
 
        normalized_sections: list[ 
            dict[str, Any] 
        ] = [] 
 
        # -------------------------------------------------------- 
        # Dictionary sections 
        # -------------------------------------------------------- 
 
        if isinstance( 
            sections_source, 
            dict, 
        ): 
 
            for ( 
                section_id, 
                section_value, 
            ) in sections_source.items(): 
 
                if isinstance( 
                    section_value, 
                    dict, 
                ): 
 
                    item = { 
                        **section_value 
                    } 
 
                    item.setdefault( 
                        "id", 
                        str(section_id), 
                    ) 
 
                    item.setdefault( 
                        "title", 
                        str(section_id), 
                    ) 
 
                    item.setdefault( 
                        "status", 
                        "complete", 
                    ) 
 
                else: 
 
                    item = { 
                        "id": str( 
                            section_id 
                        ), 
                        "title": str( 
                            section_id 
                        ), 
                        "content": ( 
                            section_value 
                            if section_value is not None 
                            else None 
                        ), 
                        "status": "complete", 
                    } 
 
                normalized_sections.append( 
                    item 
                ) 
 
        # -------------------------------------------------------- 
        # List sections 
        # -------------------------------------------------------- 
 
        elif isinstance( 
            sections_source, 
            list, 
        ): 
 
            for index, section in enumerate( 
                sections_source 
            ): 
 
                if isinstance( 
                    section, 
                    dict, 
                ): 
 
                    item = { 
                        **section 
                    } 
 
                    item.setdefault( 
                        "id", 
                        str(index), 
                    ) 
 
                    item.setdefault( 
                        "title", 
                        f"Section {index + 1}", 
                    ) 
 
                    item.setdefault( 
                        "status", 
                        "complete", 
                    ) 
 
                else: 
 
                    item = { 
                        "id": str(index), 
                        "title": ( 
                            f"Section " 
                            f"{index + 1}" 
                        ), 
                        "content": ( 
                            section 
                            if section is not None 
                            else None 
                        ), 
                        "status": "complete", 
                    } 
 
                normalized_sections.append( 
                    item 
                ) 
 
        return { 
            "title": ( 
                str(report_title) 
                if report_title is not None 
                else None 
            ), 
            "summary": ( 
                str(report_summary) 
                if report_summary is not None 
                else None 
            ), 
            "sections": self._to_json_safe( 
                normalized_sections 
            ), 
        } 
 
    # ============================================================
    # JSON Safety
    # ============================================================

    def _to_json_safe(
        self,
        value: Any,
    ) -> Any:
        """
        Convert arbitrary Python/Pydantic/ORM values into
        PostgreSQL JSON-compatible values.
        """

        if value is None:
            return None

        if hasattr(value, "model_dump"):
            try:
                return self._to_json_safe(
                    value.model_dump(mode="python")
                )
            except Exception:
                pass

        if hasattr(value, "dict") and not isinstance(value, dict):
            try:
                return self._to_json_safe(value.dict())
            except Exception:
                pass

        if is_dataclass(value):
            try:
                return self._to_json_safe(asdict(value))
            except Exception:
                pass

        if isinstance(value, Enum):
            return self._to_json_safe(value.value)

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, time):
            return value.isoformat()

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, Decimal):
            if not value.is_finite():
                logger.warning(
                    "Non-finite Decimal detected; converting to None."
                )
                return None
            return str(value)

        if isinstance(value, float):
            if not math.isfinite(value):
                logger.warning(
                    "Non-finite float detected; converting to None."
                )
                return None
            return value

        if isinstance(value, (str, int, bool)):
            return value

        if isinstance(value, dict):
            return {
                str(key): self._to_json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [
                self._to_json_safe(item)
                for item in value
            ]

        if hasattr(value, "item"):
            try:
                item = value.item()
                if item is not value:
                    return self._to_json_safe(item)
            except Exception:
                pass

        if hasattr(value, "__dict__"):
            try:
                return self._to_json_safe(vars(value))
            except Exception:
                pass

        return str(value)

    @staticmethod
    def _safe_metadata(
        metadata: Any,
    ) -> dict[str, Any]:
        """
        Return a mutable copy of research lifecycle metadata.
        """
        if not isinstance(metadata, dict):
            return {}
        return dict(metadata)
    # ============================================================ 
    # Get Research 
    # ============================================================ 
 
    async def get_research( 
        self, 
        research_id: UUID, 
    ) -> Research | None: 
 
        if research_id is None: 
            raise ValueError( 
                "research_id is required." 
            ) 
 
        if not isinstance(research_id, UUID): 
            raise ValueError( 
                f"Invalid research_id: {research_id!r}" 
            ) 
 
        return await self.repository.get_by_id( 
            research_id 
        ) 
        # ============================================================ 
        # Status 
        # ============================================================ 
 
    async def get_status( 
        self, 
        research_id: UUID, 
    ) -> ResearchStatusResponse | None: 
 
        if research_id is None: 
            raise ValueError( 
                "research_id is required." 
            ) 
 
        if not isinstance(research_id, UUID): 
            raise ValueError( 
                f"Invalid research_id: {research_id!r}" 
            ) 
 
        research = await self.repository.get_by_id( 
            research_id 
        ) 
 
        if research is None: 
            return None 
 
        metadata = self._safe_metadata( 
            research.metadata_json 
        ) 
 
        status_value = research.status 
 
        if status_value == "complete": 
            status_value = "completed" 
 
        elif status_value == "error": 
            status_value = "failed" 
 
        if status_value == "queued": 
 
            progress = 0 
 
        elif status_value == "planning": 
 
            progress = metadata.get( 
                "progress", 
                5, 
            ) 
 
        elif status_value == "running": 
 
            progress = metadata.get( 
                "progress", 
                50, 
            ) 
 
        elif status_value == "completed": 
 
            progress = 100 
 
        elif status_value == "failed": 
 
            progress = metadata.get( 
                "progress", 
                0, 
            ) 
 
        else: 
 
            progress = metadata.get( 
                "progress", 
                0, 
            ) 
 
        try: 
 
            progress = max( 
                0, 
                min( 
                    int(progress), 
                    100, 
                ), 
            ) 
 
        except ( 
            TypeError, 
            ValueError, 
        ): 
 
            progress = 0 
 
        current_stage = self._clean_string( 
            metadata.get( 
                "current_stage" 
            ) 
        ) 
 
        if not current_stage: 
 
            current_stage = { 
                "queued": "Queued", 
                "planning": "Planning", 
                "running": "Researching", 
                "completed": "Completed", 
                "failed": "Failed", 
            }.get( 
                status_value, 
                "Unknown", 
            ) 
 
        return ResearchStatusResponse( 
            research_id=research.id, 
            status=status_value, 
            progress=progress, 
            current_stage=current_stage, 
            execution_plan_id=research.execution_plan_id, 
            started_at=research.started_at, 
            completed_at=research.completed_at, 
            error=metadata.get( 
                "error" 
            ), 
        ) 
        # ============================================================ 
        # Results 
        # ============================================================ 
 
    async def get_results( 
        self, 
        research_id: UUID, 
    ) -> ResearchResultResponse | None: 
        """ 
        Load persisted ResearchResult. 
 
        Canonical result source: 
 
            research_results 
 
        NEVER: 
 
            research.metadata_json["results"] 
        """ 
 
        if research_id is None: 
            raise ValueError( 
                "research_id is required." 
            ) 
 
        if not isinstance(research_id, UUID):
            raise ValueError(
                f"Invalid research_id: {research_id!r}"
            )

        normalized_research_id = research_id

        research = ( 
            await self.repository.get_by_id( 
                normalized_research_id 
            ) 
        ) 
 
        if research is None: 
 
            logger.warning( 
                "Research not found | " 
                "research_id=%s", 
                normalized_research_id, 
            ) 
 
            return None 
 
        status_value = research.status 
 
        if status_value == "complete": 
            status_value = "completed" 
 
        elif status_value == "error": 
            status_value = "failed" 
 
        if status_value != "completed": 
 
            logger.info( 
                "Research results unavailable because " 
                "research is not completed | " 
                "research_id=%s | status=%s", 
                research.id, 
                status_value, 
            ) 
 
            return None 
 
        research_result = ( 
            await self.result_repository.get_by_research_id( 
                research.id 
            ) 
        ) 
 
        if research_result is None: 
 
            logger.warning( 
                "Research is completed but no " 
                "ResearchResult exists | " 
                "research_id=%s", 
                research.id, 
            ) 
 
            return None 
 
        # ======================================================== 
        # Canonical company identity 
        # ======================================================== 
 
        metadata = self._safe_metadata( 
            research.metadata_json 
        ) 
 
        company_id = metadata.get( 
            "company_id" 
        ) 
 
        if company_id is not None: 
 
            try: 
                company_id = int( 
                    company_id 
                ) 
 
            except ( 
                TypeError, 
                ValueError, 
            ): 
                company_id = None 
 
        company_name = self._clean_string( 
            research.company 
            or metadata.get( 
                "company" 
            ) 
        ) 
 
        ticker = self._clean_string( 
            research.ticker 
            or metadata.get( 
                "ticker" 
            ) 
        ) 
 
        industry = self._clean_string( 
            research.industry 
            or metadata.get( 
                "industry" 
            ) 
        ) 
 
        # ======================================================== 
        # Overview 
        # ======================================================== 
 
        overview_raw = ( 
            research_result.overview 
        ) 
 
        if not isinstance( 
            overview_raw, 
            dict, 
        ): 
            overview_raw = {} 
 
        overview = self._build_overview( 
            overview_raw, 
            company=company_name, 
            ticker=ticker, 
            industry=industry, 
        ) 
 
        # ======================================================== 
        # Evidence 
        # ======================================================== 
 
        evidence = self._normalize_evidence( 
            research_result.evidence 
        ) 
 
        # ======================================================== 
        # Documents 
        # ======================================================== 
 
        documents = self._normalize_documents( 
            research_result.documents 
        ) 
 
        # ======================================================== 
        # Insights 
        # ======================================================== 
 
        insights = self._normalize_insights( 
            research_result.insights 
        ) 
 
        # ======================================================== 
        # Report 
        # ======================================================== 
 
        report_raw = { 
            "title": research.title, 
            "summary": research_result.summary, 
            "sections": research_result.sections, 
        } 
 
        report = ( 
            self._normalize_report_response( 
                report_raw 
            ) 
        ) 
 
        # ======================================================== 
        # Agent Results 
        # ======================================================== 
 
        agent_results = ( 
            research_result.agent_results 
        ) 
 
        if not isinstance( 
            agent_results, 
            list, 
        ): 
            agent_results = [] 
 
        agent_results = self._to_json_safe( 
            agent_results 
        ) 
 
        # ======================================================== 
        # Citations 
        # ======================================================== 
 
        citations = ( 
            research_result.citations 
        ) 
 
        if not isinstance( 
            citations, 
            list, 
        ): 
            citations = [] 
 
        citations = self._to_json_safe( 
            citations 
        ) 
 
        # ======================================================== 
        # Response 
        # ======================================================== 
 
        response_data = { 
            "research_id": research.id, 
            "status": "completed", 
            "title": research.title, 
            "company_id": company_id, 
            "company": company_name, 
            "ticker": ticker, 
            "industry": industry, 
            "research_type": research.research_type, 
            "overview": overview, 
            "evidence": evidence, 
            "documents": documents, 
            "insights": insights, 
            "report": report, 
            "agent_results": agent_results, 
            "citations": citations, 
            "created_at": research.created_at, 
            "started_at": research.started_at, 
            "completed_at": research.completed_at, 
        } 
 
        try: 
 
            response = ( 
                ResearchResultResponse.model_validate( 
                    response_data 
                ) 
            ) 
 
        except Exception as exc: 
 
            logger.exception( 
                "ResearchResultResponse validation " 
                "failed | research_id=%s | " 
                "error=%s", 
                research.id, 
                exc, 
            ) 
 
            raise RuntimeError( 
                "Stored research results could not " 
                "be converted to " 
                "ResearchResultResponse. " 
                f"research_id={research.id}" 
            ) from exc 
 
        logger.info( 
            "Research results loaded successfully | " 
            "research_id=%s | result_id=%s | " 
            "overview=%s | evidence=%s | " 
            "documents=%s | insights=%s | " 
            "agent_results=%s | citations=%s", 
            research.id, 
            research_result.id, 
            bool( 
                research_result.overview 
            ), 
            len(evidence), 
            len(documents), 
            len(insights), 
            len(agent_results), 
            len(citations), 
        ) 
 
        return response 
 
    # ============================================================ 
    # Overview Builder 
    # ============================================================ 
 
    @staticmethod 
    def _build_overview( 
        overview: dict[str, Any], 
        *, 
        company: str | None, 
        ticker: str | None, 
        industry: str | None, 
    ) -> ResearchOverview: 
 
        if not isinstance( 
            overview, 
            dict, 
        ): 
            overview = {} 
 
        profile_raw = overview.get( 
            "profile" 
        ) 
 
        if not isinstance( 
            profile_raw, 
            dict, 
        ): 
            profile_raw = {} 
 
        profile_data = { 
            **profile_raw 
        } 
 
        if company is not None: 
            profile_data["name"] = company 
        else: 
            profile_data.setdefault( 
                "name", 
                None, 
            ) 
 
        if ticker is not None: 
            profile_data["ticker"] = ticker 
        else: 
            profile_data.setdefault( 
                "ticker", 
                None, 
            ) 
 
        if industry is not None: 
            profile_data["industry"] = industry 
        else: 
            profile_data.setdefault( 
                "industry", 
                None, 
            ) 
 
        market_raw = overview.get( 
            "market" 
        ) 
 
        if not isinstance( 
            market_raw, 
            dict, 
        ): 
            market_raw = {} 
 
        financials_raw = overview.get( 
            "financials" 
        ) 
 
        if not isinstance( 
            financials_raw, 
            dict, 
        ): 
            financials_raw = {} 
 
        return ResearchOverview( 
            profile=ResearchProfile( 
                **profile_data 
            ), 
            market={ 
                **market_raw 
            }, 
            financials={ 
                **financials_raw 
            }, 
        ) 
 
    # ============================================================ 
    # Evidence 
    # ============================================================ 
 
    @staticmethod 
    def _normalize_evidence( 
        values: Any, 
    ) -> list[ResearchEvidence]: 
 
        if not isinstance( 
            values, 
            list, 
        ): 
            return [] 
 
        normalized: list[ 
            ResearchEvidence 
        ] = [] 
 
        for index, value in enumerate( 
            values 
        ): 
 
            if isinstance( 
                value, 
                ResearchEvidence, 
            ): 
 
                normalized.append( 
                    value 
                ) 
 
                continue 
 
            if isinstance( 
                value, 
                str, 
            ): 
 
                normalized.append( 
                    ResearchEvidence( 
                        id=index, 
                        title=value, 
                        content=value, 
                    ) 
                ) 
 
                continue 
 
            if isinstance( 
                value, 
                dict, 
            ): 
 
                item = { 
                    **value 
                } 
 
                item.setdefault( 
                    "id", 
                    index, 
                ) 
 
                try: 
 
                    normalized.append( 
                        ResearchEvidence( 
                            **item 
                        ) 
                    ) 
 
                except Exception: 
 
                    logger.warning( 
                        "Skipping invalid research " 
                        "evidence | index=%s", 
                        index, 
                        exc_info=True, 
                    ) 
 
        return normalized 
 
    # ============================================================ 
    # Documents 
    # ============================================================ 
 
    @staticmethod 
    def _normalize_documents( 
        values: Any, 
    ) -> list[ResearchDocument]: 
 
        if not isinstance( 
            values, 
            list, 
        ): 
            return [] 
 
        normalized: list[ 
            ResearchDocument 
        ] = [] 
 
        for index, value in enumerate( 
            values 
        ): 
 
            if isinstance( 
                value, 
                ResearchDocument, 
            ): 
 
                normalized.append( 
                    value 
                ) 
 
                continue 
 
            if not isinstance( 
                value, 
                dict, 
            ): 
                continue 
 
            item = { 
                **value 
            } 
 
            item.setdefault( 
                "title", 
                f"Document {index + 1}", 
            ) 
 
            try: 
 
                normalized.append( 
                    ResearchDocument( 
                        **item 
                    ) 
                ) 
 
            except Exception: 
 
                logger.warning( 
                    "Skipping invalid research " 
                    "document | index=%s", 
                    index, 
                    exc_info=True, 
                ) 
 
        return normalized 
 
    # ============================================================ 
    # Insights 
    # ============================================================ 
 
    @staticmethod 
    def _normalize_insights( 
        values: Any, 
    ) -> list[ResearchInsight]: 
 
        if not isinstance( 
            values, 
            list, 
        ): 
            return [] 
 
        normalized: list[ 
            ResearchInsight 
        ] = [] 
 
        for index, value in enumerate( 
            values 
        ): 
 
            if isinstance( 
                value, 
                ResearchInsight, 
            ): 
 
                normalized.append( 
                    value 
                ) 
 
                continue 
 
            if not isinstance( 
                value, 
                dict, 
            ): 
                continue 
 
            item = { 
                **value 
            } 
 
            item.setdefault( 
                "id", 
                index, 
            ) 
 
            item.setdefault( 
                "title", 
                f"Insight {index + 1}", 
            ) 
 
            try: 
 
                normalized.append( 
                    ResearchInsight( 
                        **item 
                    ) 
                ) 
 
            except Exception: 
 
                logger.warning( 
                    "Skipping invalid research " 
                    "insight | index=%s", 
                    index, 
                    exc_info=True, 
                ) 
 
        return normalized 
 
    # ============================================================ 
    # Report Response 
    # ============================================================ 
 
    @staticmethod 
    def _normalize_report_response( 
        value: dict[str, Any], 
    ) -> ResearchReport: 
 
        if not isinstance( 
            value, 
            dict, 
        ): 
            value = {} 
 
        title = value.get( 
            "title" 
        ) 
 
        summary = value.get( 
            "summary" 
        ) 
 
        if summary is not None: 
            summary = str(summary) 
 
        sections_raw = ( 
            value.get( 
                "sections" 
            ) 
            or [] 
        ) 
 
        sections: list[ 
            ResearchReportSection 
        ] = [] 
 
        if isinstance( 
            sections_raw, 
            dict, 
        ): 
 
            iterator = sections_raw.items() 
 
        elif isinstance( 
            sections_raw, 
            list, 
        ): 
 
            iterator = enumerate( 
                sections_raw 
            ) 
 
        else: 
 
            iterator = [] 
 
        for ( 
            section_id, 
            section_value, 
        ) in iterator: 
 
            if isinstance( 
                section_value, 
                dict, 
            ): 
 
                item = { 
                    **section_value 
                } 
 
                item.setdefault( 
                    "id", 
                    str(section_id), 
                ) 
 
                item.setdefault( 
                    "title", 
                    str(section_id), 
                ) 
 
                item.setdefault( 
                    "status", 
                    "complete", 
                ) 
 
            else: 
 
                if isinstance( 
                    section_id, 
                    int, 
                ): 
 
                    section_title = ( 
                        f"Section " 
                        f"{section_id + 1}" 
                    ) 
 
                else: 
 
                    section_title = str( 
                        section_id 
                    ) 
 
                item = { 
                    "id": str( 
                        section_id 
                    ), 
                    "title": section_title, 
                    "content": ( 
                        section_value 
                        if section_value is not None 
                        else None 
                    ), 
                    "status": "complete", 
                } 
 
            item["id"] = str( 
                item.get( 
                    "id", 
                    section_id, 
                ) 
            ) 
 
            item["title"] = str( 
                item.get( 
                    "title", 
                    f"Section {section_id}", 
                ) 
            ) 
 
            try: 
 
                sections.append( 
                    ResearchReportSection( 
                        **item 
                    ) 
                ) 
 
            except Exception: 
 
                logger.warning( 
                    "Skipping invalid report " 
                    "section | id=%s", 
                    section_id, 
                    exc_info=True, 
                ) 
 
        return ResearchReport( 
            title=( 
                str(title) 
                if title is not None 
                else None 
            ), 
            summary=summary, 
            sections=sections, 
        ) 
 
    # ============================================================ 
    # String Helpers 
    # ============================================================ 
 
    @staticmethod 
    def _clean_string( 
        value: Any, 
    ) -> str | None: 
 
        if value is None: 
            return None 
 
        if not isinstance( 
            value, 
            str, 
        ): 
            value = str(value) 
 
        value = value.strip() 
 
        return value or None
