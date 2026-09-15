"""
app/agents/evidence/agent.py

Evidence Intelligence Agent.

Collects, validates, matches, and organizes evidence supporting
claims produced by upstream equity-research agents.

Execution model:

    AgentContext
        ↓
    upstream AgentResults
        ↓
    claim extraction
        ↓
    source extraction
        ↓
    evidence construction
        ↓
    EvidenceMatcher
        ↓
    validation
        ↓
    CitationManager
        ↓
    AgentResult

Important architectural rule:

    EvidenceAgent consumes the canonical AgentContext and the
    AgentResult objects already accumulated inside it.

It does NOT create another context and does NOT access the DB
directly.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.agents.base.base_agent import BaseAgent

from .citation_manager import CitationManager
from .evidence_matching import EvidenceMatcher


logger = logging.getLogger(__name__)


class EvidenceAgent(BaseAgent):
    """
    Evidence intelligence layer for equity research.

    Responsibilities
    ----------------
    - Collect claims from upstream research results.
    - Extract structured facts from upstream agent outputs.
    - Collect sources from upstream AgentResults.
    - Match claims with supporting sources.
    - Validate evidence.
    - Generate citations.
    - Enrich the shared AgentContext.
    - Produce a structured evidence package.
    """

    # =========================================================
    # Canonical Agent Identity
    # =========================================================

    agent_id = "evidence"

    name = "evidence_agent"

    category = "research"

    display_name = "Evidence Intelligence Agent"

    description = """
    Validates research claims against supporting evidence,
    evaluates source reliability, and produces citation-backed
    evidence packages for downstream research and critique.
    """

    capabilities = [
        "evidence_collection",
        "claim_evidence_matching",
        "evidence_validation",
        "source_validation",
        "citation_generation",
        "source_reliability_analysis",
        "evidence_package_generation",
    ]

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        services: AgentServices,
        evidence_matcher: EvidenceMatcher | None = None,
        citation_manager: CitationManager | None = None,
    ) -> None:
        super().__init__(
            services=services
        )

        self.matcher = (
            evidence_matcher
            if evidence_matcher is not None
            else EvidenceMatcher()
        )

        self.citation_manager = (
            citation_manager
            if citation_manager is not None
            else CitationManager()
        )

    # =========================================================
    # Main Execution
    # =========================================================

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute evidence analysis using the canonical context.
        """

        logger.info(
            "Starting EvidenceAgent | "
            "research_id=%r | "
            "task_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "context_id=%s | "
            "upstream_results=%d",
            context.research_id,
            context.task_id,
            context.company,
            context.ticker,
            id(context),
            len(context.agent_results),
        )

        # =====================================================
        # 1. Collect claims
        # =====================================================

        claims = self._collect_claims(
            context
        )

        logger.info(
            "EvidenceAgent claims collected | "
            "research_id=%r | "
            "claim_count=%d",
            context.research_id,
            len(claims),
        )

        # =====================================================
        # 2. Collect sources
        # =====================================================

        sources = self._collect_sources(
            context=context,
        )

        logger.info(
            "EvidenceAgent sources collected | "
            "research_id=%r | "
            "source_count=%d",
            context.research_id,
            len(sources),
        )

        # =====================================================
        # 3. Collect existing evidence
        # =====================================================

        existing_evidence = self._collect_evidence(
            context
        )

        # =====================================================
        # 4. Match claims against sources
        # =====================================================

        matched = await self._match_claims(
            claims=claims,
            sources=sources,
            existing_evidence=existing_evidence,
        )

        logger.info(
            "EvidenceAgent matching completed | "
            "research_id=%r | "
            "matched_count=%d",
            context.research_id,
            len(matched),
        )

        # =====================================================
        # 5. Validate
        # =====================================================

        validated = await self._validate_matches(
            matched
        )

        # =====================================================
        # 6. Generate citations
        # =====================================================

        citations = await self.citation_manager.create(
            validated
        )

        # =====================================================
        # 7. Build documents
        # =====================================================

        documents = self._collect_documents(
            sources=sources,
            evidence=validated,
        )

        # =====================================================
        # 8. Enrich shared context
        # =====================================================

        for item in validated:
            context.add_evidence(
                item
            )

        for citation in citations:
            context.add_citation(
                self._citation_value(
                    citation
                )
            )

        # =====================================================
        # 9. Build output
        # =====================================================

        output = {
            "agent": self.agent_id,
            "agent_name": self.name,
            "research_id": context.research_id,
            "task_id": context.task_id,
            "company": context.company,
            "ticker": context.ticker,

            "claims": claims,

            "matched_evidence": validated,

            "evidence": validated,

            "citations": citations,

            "documents": documents,

            "evidence_count": len(validated),

            "citation_count": len(citations),

            "document_count": len(documents),

            "status": "completed",
        }

        # =====================================================
        # 10. Build AgentResult
        # =====================================================

        confidence = self._calculate_confidence(
            validated
        )

        logger.info(
            "EvidenceAgent completed | "
            "research_id=%r | "
            "claims=%d | "
            "evidence=%d | "
            "citations=%d | "
            "documents=%d | "
            "confidence=%.3f",
            context.research_id,
            len(claims),
            len(validated),
            len(citations),
            len(documents),
            confidence,
        )

        return AgentResult.success(
            agent_name=self.agent_id,
            data=output,
            sources=self._extract_source_names(
                sources
            ),
            confidence=confidence,
            metadata={
                "claim_count": len(claims),
                "evidence_count": len(validated),
                "citation_count": len(citations),
                "document_count": len(documents),
            },
        )

    # =========================================================
    # Claim Collection
    # =========================================================

    def _collect_claims(
        self,
        context: AgentContext,
    ) -> list[dict[str, Any]]:
        """
        Collect claims from upstream AgentResults.

        Supports both:

        1. Explicit claims:
               result.data["claims"]

        2. Structured upstream outputs such as:

               financial_metrics
               conclusion
               thesis
               decision
               overall_risk
               risks
               recommendations
               findings
               analysis
               market
               valuation
               industry_metadata

        This is the important compatibility layer between
        structured research agents and the EvidenceAgent.
        """

        claims: list[dict[str, Any]] = []

        seen: set[str] = set()

        for agent_name, result in context.agent_results.items():

            if agent_name in {
                self.agent_id,
                self.name,
            }:
                continue

            if result is None:
                continue

            result_data = getattr(
                result,
                "data",
                None,
            )

            if not isinstance(
                result_data,
                dict,
            ):
                continue

            # -------------------------------------------------
            # Explicit claims
            # -------------------------------------------------

            explicit_claims = result_data.get(
                "claims",
                [],
            )

            if isinstance(
                explicit_claims,
                list,
            ):
                for claim in explicit_claims:

                    normalized = self._normalize_claim(
                        claim=claim,
                        agent_name=agent_name,
                    )

                    if normalized is not None:
                        self._append_unique_claim(
                            claims,
                            seen,
                            normalized,
                        )

            # -------------------------------------------------
            # Findings
            # -------------------------------------------------

            findings = result_data.get(
                "findings",
                [],
            )

            if isinstance(
                findings,
                list,
            ):
                for finding in findings:

                    normalized = self._normalize_claim(
                        claim=finding,
                        agent_name=agent_name,
                    )

                    if normalized is not None:
                        self._append_unique_claim(
                            claims,
                            seen,
                            normalized,
                        )

            # -------------------------------------------------
            # Structured financial metrics
            # -------------------------------------------------

            financial_metrics = result_data.get(
                "financial_metrics"
            )

            if isinstance(
                financial_metrics,
                dict,
            ):
                self._extract_metric_claims(
                    claims=claims,
                    seen=seen,
                    metrics=financial_metrics,
                    agent_name=agent_name,
                )

            # -------------------------------------------------
            # Common textual research fields
            # -------------------------------------------------

            textual_fields = (
                "conclusion",
                "thesis",
                "decision",
                "assessment",
                "analysis",
                "summary",
                "recommendation",
                "overall_risk",
                "risk_assessment",
            )

            for field in textual_fields:

                value = result_data.get(
                    field
                )

                if isinstance(
                    value,
                    str,
                ) and value.strip():

                    claim = {
                        "text": value.strip(),
                        "agent": agent_name,
                        "field": field,
                        "source_agent": agent_name,
                    }

                    self._append_unique_claim(
                        claims,
                        seen,
                        claim,
                    )

            # -------------------------------------------------
            # Common list fields
            # -------------------------------------------------

            list_fields = (
                "risks",
                "recommendations",
                "catalysts",
                "key_reasons",
                "findings",
                "scenarios",
                "trends",
                "competitors",
                "opportunities",
            )

            for field in list_fields:

                values = result_data.get(
                    field
                )

                if not isinstance(
                    values,
                    list,
                ):
                    continue

                for value in values:

                    normalized = self._normalize_claim(
                        claim=value,
                        agent_name=agent_name,
                        field=field,
                    )

                    if normalized is not None:
                        self._append_unique_claim(
                            claims,
                            seen,
                            normalized,
                        )

        # -----------------------------------------------------
        # Explicit runtime claims
        # -----------------------------------------------------

        runtime_claims = context.get_data(
            "claims",
            [],
        )

        if isinstance(
            runtime_claims,
            list,
        ):
            for claim in runtime_claims:

                normalized = self._normalize_claim(
                    claim=claim,
                    agent_name="runtime",
                )

                if normalized is not None:
                    self._append_unique_claim(
                        claims,
                        seen,
                        normalized,
                    )

        return claims

    # =========================================================
    # Claim Normalization
    # =========================================================

    @staticmethod
    def _normalize_claim(
        claim: Any,
        agent_name: str,
        field: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Normalize arbitrary upstream claim representations.
        """

        if isinstance(
            claim,
            str,
        ):
            text = claim.strip()

            if not text:
                return None

            return {
                "text": text,
                "agent": agent_name,
                "field": field,
                "source_agent": agent_name,
            }

        if isinstance(
            claim,
            dict,
        ):
            text = (
                claim.get("text")
                or claim.get("claim")
                or claim.get("statement")
                or claim.get("finding")
                or claim.get("description")
            )

            if not isinstance(
                text,
                str,
            ):
                return None

            text = text.strip()

            if not text:
                return None

            normalized = dict(
                claim
            )

            normalized["text"] = text
            normalized.setdefault(
                "agent",
                agent_name,
            )
            normalized.setdefault(
                "source_agent",
                agent_name,
            )

            if field is not None:
                normalized.setdefault(
                    "field",
                    field,
                )

            return normalized

        return None

    # =========================================================
    # Financial Metric Claims
    # =========================================================

    @staticmethod
    def _extract_metric_claims(
        claims: list[dict[str, Any]],
        seen: set[str],
        metrics: dict[str, Any],
        agent_name: str,
    ) -> None:
        """
        Convert important structured financial metrics into
        evidence-trackable claims.

        Only scalar values are converted.
        """

        preferred_metrics = (
            "current_price",
            "market_cap",
            "enterprise_value",
            "trailing_pe",
            "profit_margin",
            "operating_margin",
            "dividend_yield",
            "earnings_growth",
            "revenue_growth",
        )

        for metric_name in preferred_metrics:

            if metric_name not in metrics:
                continue

            value = metrics.get(
                metric_name
            )

            if value is None:
                continue

            if isinstance(
                value,
                (dict, list),
            ):
                continue

            label = metric_name.replace(
                "_",
                " ",
            )

            text = (
                f"{label.title()} is {value}"
            )

            claim = {
                "text": text,
                "agent": agent_name,
                "source_agent": agent_name,
                "field": "financial_metrics",
                "metric": metric_name,
                "value": value,
            }

            key = text.lower()

            if key not in seen:
                seen.add(key)
                claims.append(
                    claim
                )

    # =========================================================
    # Unique Claims
    # =========================================================

    @staticmethod
    def _append_unique_claim(
        claims: list[dict[str, Any]],
        seen: set[str],
        claim: dict[str, Any],
    ) -> None:

        text = claim.get(
            "text"
        )

        if not isinstance(
            text,
            str,
        ):
            return

        key = text.strip().lower()

        if not key:
            return

        if key in seen:
            return

        seen.add(key)

        claims.append(
            claim
        )

    # =========================================================
    # Evidence Collection
    # =========================================================

    def _collect_evidence(
        self,
        context: AgentContext,
    ) -> list[dict[str, Any]]:
        """
        Collect evidence already accumulated in context and
        runtime data.
        """

        evidence: list[dict[str, Any]] = []

        context_evidence = getattr(
            context,
            "evidence",
            [],
        )

        if isinstance(
            context_evidence,
            list,
        ):
            evidence.extend(
                item
                for item in context_evidence
                if isinstance(
                    item,
                    dict,
                )
            )

        runtime_evidence = context.get_data(
            "evidence",
            [],
        )

        if isinstance(
            runtime_evidence,
            list,
        ):
            evidence.extend(
                item
                for item in runtime_evidence
                if isinstance(
                    item,
                    dict,
                )
            )

        return evidence

    # =========================================================
    # Source Collection
    # =========================================================

    def _collect_sources(
        self,
        context: AgentContext,
    ) -> list[dict[str, Any]]:
        """
        Collect sources from ALL relevant locations.

        This is the second major fix.

        Sources may exist in:

            AgentResult.sources
            AgentResult.data["sources"]
            AgentContext.data["sources"]
            AgentContext.evidence[*]["source"]
        """

        sources: list[dict[str, Any]] = []

        seen: set[str] = set()

        # -----------------------------------------------------
        # Existing context evidence
        # -----------------------------------------------------

        context_evidence = getattr(
            context,
            "evidence",
            [],
        )

        if isinstance(
            context_evidence,
            list,
        ):
            for item in context_evidence:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                source = item.get(
                    "source"
                )

                self._append_source(
                    sources,
                    seen,
                    source,
                )

        # -----------------------------------------------------
        # Runtime sources
        # -----------------------------------------------------

        runtime_sources = context.get_data(
            "sources",
            [],
        )

        if isinstance(
            runtime_sources,
            list,
        ):
            for source in runtime_sources:

                self._append_source(
                    sources,
                    seen,
                    source,
                )

        # -----------------------------------------------------
        # Upstream AgentResults
        # -----------------------------------------------------

        for agent_name, result in context.agent_results.items():

            if agent_name in {
                self.agent_id,
                self.name,
            }:
                continue

            if result is None:
                continue

            # -------------------------------------------------
            # AgentResult.sources
            # -------------------------------------------------

            result_sources = getattr(
                result,
                "sources",
                [],
            )

            if isinstance(
                result_sources,
                list,
            ):
                for source in result_sources:

                    normalized = self._normalize_source(
                        source=source,
                        agent_name=agent_name,
                    )

                    self._append_source(
                        sources,
                        seen,
                        normalized,
                    )

            # -------------------------------------------------
            # AgentResult.data["sources"]
            # -------------------------------------------------

            result_data = getattr(
                result,
                "data",
                None,
            )

            if not isinstance(
                result_data,
                dict,
            ):
                continue

            embedded_sources = result_data.get(
                "sources",
                [],
            )

            if isinstance(
                embedded_sources,
                list,
            ):
                for source in embedded_sources:

                    normalized = self._normalize_source(
                        source=source,
                        agent_name=agent_name,
                    )

                    self._append_source(
                        sources,
                        seen,
                        normalized,
                    )

        return sources

    # =========================================================
    # Source Normalization
    # =========================================================

    @staticmethod
    def _normalize_source(
        source: Any,
        agent_name: str | None = None,
    ) -> dict[str, Any] | None:

        if isinstance(
            source,
            dict,
        ):
            normalized = dict(
                source
            )

            if agent_name:
                normalized.setdefault(
                    "agent",
                    agent_name,
                )

            if not normalized.get(
                "name"
            ):
                normalized["name"] = (
                    normalized.get("title")
                    or normalized.get("provider")
                    or normalized.get("url")
                    or agent_name
                    or "Unknown Source"
                )

            return normalized

        if isinstance(
            source,
            str,
        ) and source.strip():

            return {
                "name": source.strip(),
                "agent": agent_name,
            }

        return None

    @staticmethod
    def _append_source(
        sources: list[dict[str, Any]],
        seen: set[str],
        source: Any,
    ) -> None:

        if not isinstance(
            source,
            dict,
        ):
            return

        identity = (
            str(
                source.get("url")
                or source.get("name")
                or source.get("provider")
                or source
            )
            .strip()
            .lower()
        )

        if not identity:
            return

        if identity in seen:
            return

        seen.add(
            identity
        )

        sources.append(
            source
        )

    # =========================================================
    # Claim Matching
    # =========================================================

    async def _match_claims(
        self,
        claims: list[dict[str, Any]],
        sources: list[dict[str, Any]],
        existing_evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Match claims to evidence.

        First use direct source relationships from the upstream
        agent. Then fall back to EvidenceMatcher.
        """

        matched: list[dict[str, Any]] = []

        for claim in claims:

            source_agent = claim.get(
                "source_agent"
            )

            metric = claim.get(
                "metric"
            )

            candidate_sources = [
                source
                for source in sources
                if (
                    source.get("agent")
                    == source_agent
                    or source.get("source_agent")
                    == source_agent
                )
            ]

            # -------------------------------------------------
            # If there is no agent-specific source, use all
            # available sources.
            # -------------------------------------------------

            if not candidate_sources:
                candidate_sources = sources

            # -------------------------------------------------
            # Prefer structured source attached to existing
            # evidence.
            # -------------------------------------------------

            direct_source = self._find_direct_evidence_source(
                claim=claim,
                existing_evidence=existing_evidence,
            )

            if direct_source is not None:

                candidate_sources = [
                    direct_source
                ]

            # -------------------------------------------------
            # Direct structured-source matching
            # -------------------------------------------------

            for source in candidate_sources:

                matched.append(
                    {
                        "claim": claim.get(
                            "text"
                        ),

                        "claim_data": claim,

                        "source": (
                            source.get("name")
                            or source.get("title")
                            or source.get("provider")
                        ),

                        "provider": source.get(
                            "provider"
                        ),

                        "url": source.get(
                            "url"
                        ),

                        "document": (
                            source.get("document")
                            or source.get("title")
                        ),

                        "date": source.get(
                            "date"
                        ),

                        "content": (
                            source.get("content")
                            or source.get("excerpt")
                            or source.get("description")
                        ),

                        "metric": metric,

                        "source_metadata": source,

                        "confidence": (
                            0.85
                            if source
                            else 0.0
                        ),
                    }
                )

                # One source is enough for each claim.
                break

            # -------------------------------------------------
            # No source available -> fallback matcher
            # -------------------------------------------------

            if not candidate_sources:

                fallback = await self.matcher.match(
                    [claim],
                    sources,
                )

                matched.extend(
                    fallback
                )

        return matched

    @staticmethod
    def _find_direct_evidence_source(
        claim: dict[str, Any],
        existing_evidence: list[dict[str, Any]],
    ) -> dict[str, Any] | None:

        source_agent = claim.get(
            "source_agent"
        )

        for item in existing_evidence:

            if not isinstance(
                item,
                dict,
            ):
                continue

            source = item.get(
                "source"
            )

            if not isinstance(
                source,
                dict,
            ):
                continue

            if (
                source_agent
                and source.get("agent")
                == source_agent
            ):
                return source

        return None

    # =========================================================
    # Validation
    # =========================================================

    async def _validate_matches(
        self,
        matched: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Validate matched claim/evidence pairs.

        IMPORTANT:
        EvidenceMatcher.verify() expects a claim dictionary,
        not a string.
        """

        validated: list[dict[str, Any]] = []

        for item in matched:

            if not isinstance(
                item,
                dict,
            ):
                continue

            claim_data = item.get(
                "claim_data"
            )

            if not isinstance(
                claim_data,
                dict,
            ):
                claim_data = {
                    "text": item.get(
                        "claim"
                    )
                }

            claim_text = claim_data.get(
                "text"
            )

            if not claim_text:
                continue

            # -------------------------------------------------
            # A source is required for evidence-backed status.
            # -------------------------------------------------

            source = (
                item.get("source")
                or item.get("provider")
                or item.get("url")
            )

            if not source:
                continue

            try:
                verification = await self.matcher.verify(
                    {
                        **claim_data,
                        "evidence": {
                            "source": source,
                            "url": item.get(
                                "url"
                            ),
                            "document": item.get(
                                "document"
                            ),
                            "content": item.get(
                                "content"
                            ),
                        },
                    }
                )

            except Exception:
                logger.exception(
                    "Failed to verify evidence claim"
                )

                verification = {
                    "verified": False,
                    "error": (
                        "Evidence verification failed"
                    ),
                }

            enriched = {
                **item,
                "verification": verification,
            }

            validated.append(
                enriched
            )

        return validated

    # =========================================================
    # Documents
    # =========================================================

    @staticmethod
    def _collect_documents(
        sources: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Build document records from real source metadata.

        No fake documents are created.

        A source is considered a document when it has enough
        identifying metadata such as title/name/url/document.
        """

        documents: list[dict[str, Any]] = []

        seen: set[str] = set()

        for source in sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            title = (
                source.get("title")
                or source.get("document")
                or source.get("name")
                or source.get("provider")
            )

            url = source.get(
                "url"
            )

            provider = source.get(
                "provider"
            )

            if not title and not url:
                continue

            identity = str(
                url
                or title
                or provider
            ).strip().lower()

            if identity in seen:
                continue

            seen.add(
                identity
            )

            documents.append(
                {
                    "id": source.get(
                        "id"
                    ),
                    "title": str(
                        title
                        or "Research Source"
                    ),
                    "type": source.get(
                        "type"
                    ) or "source",
                    "url": url,
                    "date": source.get(
                        "date"
                    ),
                    "source": (
                        provider
                        or source.get(
                            "name"
                        )
                    ),
                    "description": (
                        source.get(
                            "description"
                        )
                        or source.get(
                            "excerpt"
                        )
                    ),
                    "metadata": dict(
                        source
                    ),
                }
            )

        # -----------------------------------------------------
        # Also derive documents from matched evidence.
        # -----------------------------------------------------

        for item in evidence:

            if not isinstance(
                item,
                dict,
            ):
                continue

            title = (
                item.get("document")
                or item.get("source")
            )

            url = item.get(
                "url"
            )

            if not title and not url:
                continue

            identity = str(
                url
                or title
            ).strip().lower()

            if identity in seen:
                continue

            seen.add(
                identity
            )

            documents.append(
                {
                    "id": None,
                    "title": str(
                        title
                    ),
                    "type": "evidence_source",
                    "url": url,
                    "date": item.get(
                        "date"
                    ),
                    "source": item.get(
                        "provider"
                    ) or item.get(
                        "source"
                    ),
                    "description": item.get(
                        "content"
                    ),
                    "metadata": {
                        "from_evidence": True
                    },
                }
            )

        return documents

    # =========================================================
    # Helpers
    # =========================================================

    @staticmethod
    def _citation_value(
        citation: Any,
    ) -> str:

        if isinstance(
            citation,
            str,
        ):
            return citation

        if isinstance(
            citation,
            dict,
        ):
            return str(
                citation.get(
                    "citation"
                )
                or citation.get(
                    "url"
                )
                or citation
            )

        return str(
            citation
        )

    # =========================================================

    @staticmethod
    def _extract_source_names(
        sources: list[dict[str, Any]],
    ) -> list[str]:

        result: list[str] = []

        seen: set[str] = set()

        for source in sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            value = (
                source.get("title")
                or source.get("name")
                or source.get("provider")
                or source.get("url")
            )

            if not value:
                continue

            value = str(
                value
            )

            if value in seen:
                continue

            seen.add(
                value
            )

            result.append(
                value
            )

        return result

    # =========================================================

    @staticmethod
    def _calculate_confidence(
        evidence: list[dict[str, Any]],
    ) -> float:
        """
        Calculate:

            verified evidence / total evidence
        """

        if not evidence:
            return 0.0

        verified = 0

        for item in evidence:

            if not isinstance(
                item,
                dict,
            ):
                continue

            verification = item.get(
                "verification",
                {},
            )

            if (
                isinstance(
                    verification,
                    dict,
                )
                and verification.get(
                    "verified",
                    False,
                )
            ):
                verified += 1

        return verified / len(
            evidence
        )