"""
app/agents/critic/agent.py

Critic / Research Quality Control Agent.

Canonical architecture:

    ExecutionEngine
          |
          v
      AgentContext
          |
          v
      CriticAgent
          |
          +── upstream AgentResults
          +── VerificationEngine
          +── HallucinationDetector
          +── deterministic quality evaluation
          |
          v
      AgentResult

Responsibilities
----------------
- Evaluate research outputs produced by upstream agents.
- Verify claims.
- Detect potential hallucinations.
- Evaluate evidence quality.
- Evaluate reasoning/reliability signals.
- Produce a canonical AgentResult.
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.agents.base.base_agent import BaseAgent

from .verification import VerificationEngine
from .hallucination import HallucinationDetector


logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    """
    Research quality-control agent.

    The CriticAgent consumes upstream research through the canonical
    AgentContext and returns a canonical AgentResult.

    It intentionally does not own orchestration. Dependency resolution,
    task scheduling, lifecycle management, and execution are handled by
    AgentManager / ExecutionEngine.
    """

    # =====================================================================
    # Agent metadata
    # =====================================================================

    agent_id = "critic"

    category = "research"

    display_name = "Research Critic Agent"

    description = (
        "Evaluates research outputs for factual reliability, "
        "evidence quality, reasoning quality, hallucination risk, "
        "and overall research integrity."
    )

    capabilities = [
        "research.critique",
        "research.verification",
        "research.hallucination_detection",
        "research.quality_control",
    ]

    # =====================================================================
    # Initialization
    # =====================================================================

    def __init__(
        self,
        services: AgentServices,
        verifier: VerificationEngine | None = None,
        hallucination_detector: HallucinationDetector | None = None,
    ) -> None:
        """
        Initialize CriticAgent.

        AgentManager injects the canonical AgentServices instance.
        """

        super().__init__(
            services=services,
        )

        self.verifier = (
            verifier
            if verifier is not None
            else VerificationEngine()
        )

        self.hallucination_detector = (
            hallucination_detector
            if hallucination_detector is not None
            else HallucinationDetector()
        )

    # =====================================================================
    # Canonical execution entrypoint
    # =====================================================================

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Canonical BaseAgent execution entrypoint.

        Reads upstream research from AgentContext, performs verification
        and hallucination detection, and returns AgentResult.
        """

        if context is None:
            raise ValueError(
                "AgentContext is required for CriticAgent"
            )

        task_id = getattr(
            context,
            "task_id",
            None,
        )

        research_id = getattr(
            context,
            "research_id",
            None,
        )

        logger.info(
            "CRITIC AGENT START | "
            "context_object_id=%s | "
            "task_id=%r | "
            "research_id=%r",
            id(context),
            task_id,
            research_id,
        )

        try:
            # =============================================================
            # 1. Collect upstream research
            # =============================================================

            research_output = self._collect_research_output(
                context=context,
            )

            if not research_output:
                raise ValueError(
                    "No upstream research output is available "
                    "in AgentContext for CriticAgent."
                )

            # =============================================================
            # 2. Run critic analysis
            # =============================================================

            result = await self.analyze(
                research_output=research_output,
                context=context,
            )

            # =============================================================
            # 3. Store critic result in context
            # =============================================================

            context.set_data(
                "critic",
                result,
            )

            context.set_data(
                "critic_analysis",
                result,
            )

            # =============================================================
            # 4. Return canonical AgentResult
            # =============================================================

            logger.info(
                "CRITIC AGENT COMPLETED | "
                "context_object_id=%s | "
                "task_id=%r | "
                "research_id=%r",
                id(context),
                task_id,
                research_id,
            )

            return AgentResult.success(
                agent_name=self.agent_id,
                task_id=task_id,
                data=result,
            )

        except Exception as exc:

            logger.exception(
                "CRITIC AGENT FAILED | "
                "task_id=%r | "
                "research_id=%r | "
                "exception_type=%s | "
                "exception=%s",
                task_id,
                research_id,
                type(exc).__name__,
                str(exc),
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=task_id,
                error=str(exc),
            )

    # =====================================================================
    # Research output resolution
    # =====================================================================

    def _collect_research_output(
        self,
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Collect upstream research from AgentContext.

        The critic should primarily consume canonical AgentContext data
        rather than directly reaching into repositories or orchestrators.
        """

        output: dict[str, Any] = {}

        # -----------------------------------------------------------------
        # 1. Canonical context data
        # -----------------------------------------------------------------

        context_data = getattr(
            context,
            "data",
            None,
        )

        if isinstance(
            context_data,
            dict,
        ):
            output.update(
                context_data
            )

        # -----------------------------------------------------------------
        # 2. Upstream AgentResults
        # -----------------------------------------------------------------

        agent_results = getattr(
            context,
            "agent_results",
            None,
        )

        if agent_results:

            output[
                "agent_results"
            ] = self._serialize_agent_results(
                agent_results
            )

        # -----------------------------------------------------------------
        # 3. Explicit research output
        # -----------------------------------------------------------------

        research_output = getattr(
            context,
            "research_output",
            None,
        )

        if isinstance(
            research_output,
            dict,
        ):

            output[
                "research_output"
            ] = research_output

        # -----------------------------------------------------------------
        # 4. Metadata fallback
        # -----------------------------------------------------------------

        metadata = getattr(
            context,
            "metadata",
            None,
        )

        if isinstance(
            metadata,
            dict,
        ):

            upstream = metadata.get(
                "research_output"
            )

            if isinstance(
                upstream,
                dict,
            ):

                output[
                    "research_output"
                ] = upstream

        return output

    # =====================================================================
    # Serialization
    # =====================================================================

    def _serialize_agent_results(
        self,
        agent_results: Any,
    ) -> Any:
        """
        Convert AgentResult objects and nested structures into
        serialization-safe dictionaries.
        """

        if isinstance(
            agent_results,
            dict,
        ):

            return {
                key: self._serialize_agent_results(
                    value
                )
                for key, value in agent_results.items()
            }

        if isinstance(
            agent_results,
            list,
        ):

            return [
                self._serialize_agent_results(
                    item
                )
                for item in agent_results
            ]

        if isinstance(
            agent_results,
            tuple,
        ):

            return [
                self._serialize_agent_results(
                    item
                )
                for item in agent_results
            ]

        if isinstance(
            agent_results,
            AgentResult,
        ):

            return {
                "agent_name": agent_results.agent_name,
                "status": str(
                    agent_results.status
                ),
                "task_id": agent_results.task_id,
                "data": agent_results.data,
                "sources": agent_results.sources,
                "confidence": agent_results.confidence,
                "reasoning": agent_results.reasoning,
                "error": agent_results.error,
                "metadata": agent_results.metadata,
            }

        if hasattr(
            agent_results,
            "model_dump",
        ):

            try:
                return agent_results.model_dump(
                    mode="json"
                )
            except TypeError:
                return agent_results.model_dump()

        return agent_results

    # =====================================================================
    # Main critic workflow
    # =====================================================================

    async def analyze(
        self,
        research_output: dict[str, Any],
        context: AgentContext | None = None,
    ) -> dict[str, Any]:
        """
        Main critic workflow.

        Performs:

            1. Claim extraction
            2. Claim verification
            3. Hallucination detection
            4. Quality scoring
            5. Structured result generation
        """

        if not isinstance(
            research_output,
            dict,
        ):
            raise TypeError(
                "research_output must be a dictionary."
            )

        # ================================================================
        # 1. Extract claims
        # ================================================================

        claims = self._extract_claims(
            research_output
        )

        # ================================================================
        # 2. Verification
        # ================================================================

        verification_result = await self._verify_claims(
            claims=claims,
            context=context,
        )

        # ================================================================
        # 3. Hallucination detection
        # ================================================================

        hallucination_result = await self._detect_hallucinations(
            research_output=research_output,
            context=context,
        )

        # ================================================================
        # 4. Deterministic quality assessment
        # ================================================================

        quality = self._calculate_quality(
            verification_result=verification_result,
            hallucination_result=hallucination_result,
            claims=claims,
        )

        # ================================================================
        # 5. Final structured result
        # ================================================================

        return {
            "agent": self.agent_id,

            "status": "completed",

            "claims": claims,

            "verification": verification_result,

            "hallucination": hallucination_result,

            "quality": quality,

            "metadata": {
                "critic_version": "canonical_v1",
                "claim_count": len(claims),
                "research_id": (
                    getattr(
                        context,
                        "research_id",
                        None,
                    )
                    if context is not None
                    else None
                ),
            },
        }

    # =====================================================================
    # Claim extraction
    # =====================================================================

    def _extract_claims(
        self,
        research_output: dict[str, Any],
    ) -> list[Any]:
        """
        Extract claims from upstream research.

        If an explicit claims collection exists, use it.

        Otherwise preserve the research output for the verification
        engine rather than inventing claims.
        """

        claims = research_output.get(
            "claims"
        )

        if isinstance(
            claims,
            list,
        ):
            return claims

        if isinstance(
            claims,
            tuple,
        ):
            return list(
                claims
            )

        if claims is not None:
            return [
                claims
            ]

        # Some upstream agents may place claims under research output.
        nested = research_output.get(
            "research_output"
        )

        if isinstance(
            nested,
            dict,
        ):

            nested_claims = nested.get(
                "claims"
            )

            if isinstance(
                nested_claims,
                list,
            ):
                return nested_claims

            if nested_claims is not None:
                return [
                    nested_claims
                ]

        return []

    # =====================================================================
    # Verification
    # =====================================================================

    async def _verify_claims(
        self,
        claims: list[Any],
        context: AgentContext | None,
    ) -> Any:
        """
        Execute VerificationEngine with compatibility handling for
        supported verification signatures.
        """

        verify = getattr(
            self.verifier,
            "verify",
            None,
        )

        if not callable(
            verify
        ):
            raise AttributeError(
                "VerificationEngine does not expose verify()."
            )

        # ---------------------------------------------------------------
        # Preferred signature
        # ---------------------------------------------------------------

        try:

            value = verify(
                claims,
                context=context,
            )

            if inspect.isawaitable(
                value
            ):
                return await value

            return value

        except TypeError:
            pass

        # ---------------------------------------------------------------
        # Claims-only legacy signature
        # ---------------------------------------------------------------

        value = verify(
            claims
        )

        if inspect.isawaitable(
            value
        ):
            return await value

        return value

    # =====================================================================
    # Hallucination detection
    # =====================================================================

    async def _detect_hallucinations(
        self,
        research_output: dict[str, Any],
        context: AgentContext | None,
    ) -> Any:
        """
        Execute HallucinationDetector with compatibility handling.
        """

        detect = getattr(
            self.hallucination_detector,
            "detect",
            None,
        )

        if not callable(
            detect
        ):
            raise AttributeError(
                "HallucinationDetector does not expose detect()."
            )

        # ---------------------------------------------------------------
        # Preferred signature
        # ---------------------------------------------------------------

        try:

            value = detect(
                research_output,
                context=context,
            )

            if inspect.isawaitable(
                value
            ):
                return await value

            return value

        except TypeError:
            pass

        # ---------------------------------------------------------------
        # Legacy signature
        # ---------------------------------------------------------------

        value = detect(
            research_output
        )

        if inspect.isawaitable(
            value
        ):
            return await value

        return value

    # =====================================================================
    # Quality scoring
    # =====================================================================

    def _calculate_quality(
        self,
        verification_result: Any,
        hallucination_result: Any,
        claims: list[Any],
    ) -> dict[str, Any]:
        """
        Calculate deterministic quality metadata.

        This intentionally remains conservative.

        The critic does not invent confidence values when the underlying
        verification/detection engines do not expose numeric scores.
        """

        verification_score = self._extract_score(
            verification_result,
            keys=(
                "score",
                "verification_score",
                "accuracy_score",
                "confidence",
            ),
        )

        hallucination_score = self._extract_score(
            hallucination_result,
            keys=(
                "score",
                "hallucination_score",
                "risk_score",
                "confidence",
            ),
        )

        return {
            "claim_count": len(
                claims
            ),
            "verification_score": verification_score,
            "hallucination_score": hallucination_score,
            "assessment": self._derive_assessment(
                verification_score=verification_score,
                hallucination_score=hallucination_score,
            ),
        }

    # =====================================================================
    # Score extraction
    # =====================================================================

    def _extract_score(
        self,
        value: Any,
        keys: tuple[str, ...],
    ) -> float | None:
        """
        Safely extract a numeric score from a dictionary or Pydantic model.
        """

        if value is None:
            return None

        if isinstance(
            value,
            dict,
        ):

            for key in keys:

                raw = value.get(
                    key
                )

                score = self._to_float(
                    raw
                )

                if score is not None:
                    return score

            return None

        if hasattr(
            value,
            "model_dump",
        ):

            try:
                return self._extract_score(
                    value.model_dump(),
                    keys,
                )
            except Exception:
                return None

        for key in keys:

            raw = getattr(
                value,
                key,
                None,
            )

            score = self._to_float(
                raw
            )

            if score is not None:
                return score

        return None

    # =====================================================================
    # Numeric conversion
    # =====================================================================

    def _to_float(
        self,
        value: Any,
    ) -> float | None:
        """
        Convert a value to float when possible.
        """

        if value is None:
            return None

        if isinstance(
            value,
            bool,
        ):
            return None

        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

    # =====================================================================
    # Assessment
    # =====================================================================

    def _derive_assessment(
        self,
        verification_score: float | None,
        hallucination_score: float | None,
    ) -> str:
        """
        Produce a conservative quality label.

        If the underlying engines do not provide numeric scores,
        the result remains "review_required".
        """

        if (
            verification_score is None
            and hallucination_score is None
        ):
            return "review_required"

        # Higher verification score is assumed to be better.
        # Higher hallucination score is assumed to represent greater
        # hallucination risk.

        if verification_score is not None:

            if verification_score < 0.5:
                return "poor"

            if verification_score < 0.75:
                return "moderate"

        if hallucination_score is not None:

            if hallucination_score >= 0.75:
                return "poor"

            if hallucination_score >= 0.5:
                return "moderate"

        return "good"

    # =====================================================================
    # Compatibility API
    # =====================================================================

    async def review_agent_output(
        self,
        agent_name: str,
        output: dict[str, Any],
        context: AgentContext | None = None,
    ) -> dict[str, Any]:
        """
        Compatibility helper for direct callers.

        Canonical runtime execution should use run(context).
        """

        result = await self.analyze(
            research_output=output,
            context=context,
        )

        result[
            "reviewed_agent"
        ] = agent_name

        return result