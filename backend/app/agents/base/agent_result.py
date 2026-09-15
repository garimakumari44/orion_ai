"""
app/agents/base/agent_result.py

Agent Result
============

Canonical normalized output returned by every agent.

AgentResult is the universal result contract between:

    Specialized Agent
          |
          v
      BaseAgent
          |
          v
     AgentManager
          |
          v
    ExecutionEngine
          |
          v
      AgentContext

Design Principles
-----------------

1. Every agent returns AgentResult.
2. Success and failure construction is centralized here.
3. AgentResult contains normalized execution metadata.
4. AgentResult is independent of specialized agents.
5. AgentResult remains JSON-serializable.
6. Research-specific structured fields are part of the canonical
   result contract because downstream agents may need to synthesize
   findings, evidence, and citations.
7. Non-JSON-safe values are sanitized at the AgentResult boundary.
8. NaN, +inf, -inf, pandas.NA, numpy scalar values, numpy arrays,
   timestamps, sets, tuples, and similar provider values cannot leak
   through the canonical result contract.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID


logger = logging.getLogger(__name__)


# ============================================================================
# Agent Status
# ============================================================================


class AgentStatus(str, Enum):
    """
    Canonical lifecycle status for an agent execution result.
    """

    COMPLETED = "completed"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"


# ============================================================================
# Agent Result
# ============================================================================


@dataclass
class AgentResult:
    """
    Canonical normalized output returned by every agent.

    The result contains both generic execution metadata and
    structured research artifacts.

    Generic contract
    ----------------
    agent_name
    status
    task_id
    data
    confidence
    reasoning
    error
    execution_time
    timestamp
    metadata

    Research contract
    -----------------
    findings
    evidence
    citations
    sources

    All structured fields are sanitized through the canonical
    JSON-safety boundary before being stored in AgentResult.

    Non-JSON-safe values such as:

        NaN
        +inf
        -inf
        pandas.NA
        numpy.nan
        numpy scalar values
        numpy arrays
        Decimal
        datetime/date/time
        UUID
        tuples
        sets
        arbitrary objects

    are converted into JSON-compatible values.

    Floating-point non-finite values are converted to None.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    agent_name: str

    # ------------------------------------------------------------------
    # Execution state
    # ------------------------------------------------------------------

    status: AgentStatus = AgentStatus.COMPLETED

    # ------------------------------------------------------------------
    # Task identity
    # ------------------------------------------------------------------

    task_id: str | None = None

    # ------------------------------------------------------------------
    # Primary agent output
    # ------------------------------------------------------------------

    data: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Research findings
    # ------------------------------------------------------------------

    findings: list[Any] = field(
        default_factory=list
    )

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    evidence: list[Any] = field(
        default_factory=list
    )

    # ------------------------------------------------------------------
    # Citations
    # ------------------------------------------------------------------

    citations: list[Any] = field(
        default_factory=list
    )

    # ------------------------------------------------------------------
    # Sources
    #
    # Kept separately from evidence/citations because sources can
    # represent provider/document/source identifiers that are not
    # necessarily complete evidence objects or citation objects.
    # ------------------------------------------------------------------

    sources: list[str] = field(
        default_factory=list
    )

    # ------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------

    confidence: float = 0.0

    reasoning: str | None = None

    # ------------------------------------------------------------------
    # Failure information
    # ------------------------------------------------------------------

    error: str | None = None

    # ------------------------------------------------------------------
    # Execution metadata
    # ------------------------------------------------------------------

    execution_time: float | None = None

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ==================================================================
    # Constructors
    # ==================================================================

    @classmethod
    def success(
        cls,
        agent_name: str,
        data: dict[str, Any],
        *,
        task_id: str | None = None,
        findings: list[Any] | None = None,
        evidence: list[Any] | None = None,
        citations: list[Any] | None = None,
        sources: list[str] | None = None,
        confidence: float = 1.0,
        reasoning: str | None = None,
        execution_time: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentResult:
        """
        Construct a successful AgentResult.

        All structured values pass through the canonical
        JSON-safety sanitizer before being stored.

        Example
        -------

        return AgentResult.success(
            agent_name=self.agent_id,
            task_id=context.task_id,
            data={
                "analysis": analysis,
            },
            findings=findings,
            evidence=evidence,
            citations=citations,
        )

        Notes
        -----

        Non-finite floating-point values such as:

            float("nan")
            float("inf")
            float("-inf")

        are converted to None.

        Provider-specific values such as pandas.NA and numpy
        scalar values are also normalized.
        """

        # --------------------------------------------------------------
        # Validate agent name
        # --------------------------------------------------------------

        if not isinstance(
            agent_name,
            str,
        ) or not agent_name.strip():
            raise ValueError(
                "agent_name must be a non-empty string."
            )

        # --------------------------------------------------------------
        # Validate primary data
        # --------------------------------------------------------------

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "AgentResult.success() requires data to be a dict."
            )

        # --------------------------------------------------------------
        # Normalize confidence BEFORE constructing the result.
        #
        # This also prevents NaN / inf from entering the canonical
        # confidence field.
        # --------------------------------------------------------------

        normalized_confidence = cls._normalize_confidence(
            confidence
        )

        # --------------------------------------------------------------
        # Normalize execution time.
        # --------------------------------------------------------------

        normalized_execution_time = cls._normalize_execution_time(
            execution_time
        )

        # --------------------------------------------------------------
        # Normalize task ID.
        # --------------------------------------------------------------

        normalized_task_id = cls._normalize_optional_string(
            task_id
        )

        # --------------------------------------------------------------
        # Normalize reasoning.
        # --------------------------------------------------------------

        normalized_reasoning = cls._normalize_optional_string(
            reasoning
        )

        # --------------------------------------------------------------
        # Construct result.
        #
        # Every structured payload is recursively sanitized.
        # --------------------------------------------------------------

        return cls(
            agent_name=agent_name.strip(),
            status=AgentStatus.COMPLETED,
            task_id=normalized_task_id,

            data=cls._sanitize_dict(
                data
            ),

            findings=cls._sanitize_list(
                findings or []
            ),

            evidence=cls._sanitize_list(
                evidence or []
            ),

            citations=cls._sanitize_list(
                citations or []
            ),

            sources=cls._normalize_sources(
                sources
            ),

            confidence=normalized_confidence,

            reasoning=normalized_reasoning,

            error=None,

            execution_time=normalized_execution_time,

            metadata=cls._sanitize_dict(
                metadata or {}
            ),
        )

    @classmethod
    def failure(
        cls,
        agent_name: str,
        error: str,
        *,
        task_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentResult:
        """
        Construct a failed AgentResult.

        Failure results intentionally contain empty research
        artifacts so downstream consumers can safely inspect the
        canonical fields without encountering AttributeError.

        Metadata is recursively sanitized before crossing the
        AgentResult boundary.
        """

        # --------------------------------------------------------------
        # Validate agent name
        # --------------------------------------------------------------

        if not isinstance(
            agent_name,
            str,
        ) or not agent_name.strip():
            raise ValueError(
                "agent_name must be a non-empty string."
            )

        # --------------------------------------------------------------
        # Normalize error
        # --------------------------------------------------------------

        if error is None:
            error = "Unknown agent execution error."

        normalized_error = cls._safe_string(
            error
        )

        # --------------------------------------------------------------
        # Normalize task ID
        # --------------------------------------------------------------

        normalized_task_id = cls._normalize_optional_string(
            task_id
        )

        # --------------------------------------------------------------
        # Construct failed result.
        # --------------------------------------------------------------

        return cls(
            agent_name=agent_name.strip(),
            status=AgentStatus.FAILED,
            task_id=normalized_task_id,
            data={},
            findings=[],
            evidence=[],
            citations=[],
            sources=[],
            confidence=0.0,
            reasoning=None,
            error=normalized_error,
            execution_time=None,
            metadata=cls._sanitize_dict(
                metadata or {}
            ),
        )

    # ==================================================================
    # Status Helpers
    # ==================================================================

    @property
    def succeeded(self) -> bool:
        """
        Return True when the agent completed successfully.
        """

        return self.status == AgentStatus.COMPLETED

    @property
    def failed(self) -> bool:
        """
        Return True when the agent failed.
        """

        return self.status == AgentStatus.FAILED

    @property
    def running(self) -> bool:
        """
        Return True when the result represents a running execution.
        """

        return self.status == AgentStatus.RUNNING

    @property
    def pending(self) -> bool:
        """
        Return True when the result represents a pending execution.
        """

        return self.status == AgentStatus.PENDING

    @property
    def completed(self) -> bool:
        """
        Alias for succeeded.
        """

        return self.status == AgentStatus.COMPLETED

    # ==================================================================
    # Serialization
    # ==================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the result into a guaranteed JSON-safe dictionary.

        The method performs a final defensive sanitization pass.

        This is intentionally done even though constructors already
        sanitize values because AgentResult is mutable and callers
        may modify fields after construction.

        Therefore:

            AgentResult.success(...)
                    |
                    v
            sanitized AgentResult
                    |
                    v
            caller may mutate fields
                    |
                    v
                to_dict()
                    |
                    v
            final JSON-safe boundary
        """

        result = {
            "agent_name": self.agent_name,
            "status": (
                self.status.value
                if isinstance(
                    self.status,
                    AgentStatus,
                )
                else str(self.status)
            ),
            "task_id": self.task_id,
            "data": self.data,
            "findings": list(self.findings),
            "evidence": list(self.evidence),
            "citations": list(self.citations),
            "sources": list(self.sources),
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }

        return self._sanitize_dict(
            result
        )

    # ==================================================================
    # JSON Validation
    # ==================================================================

    def ensure_json_safe(self) -> dict[str, Any]:
        """
        Return the final JSON-safe representation.

        This method is an explicit serialization boundary for
        callers that want to verify the result before persistence
        or API transport.
        """

        sanitized = self.to_dict()

        try:
            json.dumps(
                sanitized,
                allow_nan=False,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "AgentResult contains a value that could not be "
                "normalized into valid JSON."
            ) from exc

        return sanitized

    # ==================================================================
    # Internal Validation
    # ==================================================================

    @staticmethod
    def _normalize_confidence(
        confidence: float,
    ) -> float:
        """
        Normalize confidence into the canonical range [0.0, 1.0].

        NaN and infinity are rejected because confidence is a
        canonical scalar field and silently converting them to
        None would violate the declared float contract.
        """

        try:
            value = float(
                confidence
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                "confidence must be a numeric value."
            ) from exc

        if not math.isfinite(
            value
        ):
            raise ValueError(
                "confidence must be a finite numeric value."
            )

        if value < 0.0 or value > 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0."
            )

        return value

    @staticmethod
    def _normalize_execution_time(
        execution_time: float | None,
    ) -> float | None:
        """
        Normalize execution time.

        None remains None.

        Finite numeric values are converted to float.

        NaN and infinities become None because execution time is
        optional telemetry and has no meaningful representation
        when non-finite.
        """

        if execution_time is None:
            return None

        try:
            value = float(
                execution_time
            )
        except (
            TypeError,
            ValueError,
        ):
            logger.warning(
                "Invalid execution_time=%r. "
                "Replacing with None.",
                execution_time,
            )
            return None

        if not math.isfinite(
            value
        ):
            return None

        return value

    # ==================================================================
    # JSON-Safety Sanitization
    # ==================================================================

    @classmethod
    def _sanitize_value(
        cls,
        value: Any,
        *,
        _seen: set[int] | None = None,
    ) -> Any:
        """
        Recursively convert arbitrary provider/agent values into
        JSON-safe Python values.

        Conversion rules
        ----------------

        None
            -> None

        bool
            -> bool

        str
            -> str

        int
            -> int

        finite float
            -> float

        NaN / +inf / -inf
            -> None

        Enum
            -> sanitized enum value

        datetime/date/time
            -> ISO-8601 string

        UUID
            -> string

        Decimal
            -> finite float, otherwise None

        dict
            -> sanitized dict with string keys

        list / tuple / set
            -> sanitized list

        numpy scalar
            -> converted through .item()

        pandas.NA / pandas.NaT
            -> None

        numpy array / pandas Series
            -> list

        arbitrary object
            -> sanitized __dict__ when available

        unsupported object
            -> string representation

        The sanitizer is intentionally defensive because financial
        providers such as yfinance commonly return numpy/pandas
        values that are not directly JSON serializable.
        """

        # --------------------------------------------------------------
        # Initialize recursion guard.
        # --------------------------------------------------------------

        if _seen is None:
            _seen = set()

        # --------------------------------------------------------------
        # None
        # --------------------------------------------------------------

        if value is None:
            return None

        # --------------------------------------------------------------
        # Primitive JSON types
        # --------------------------------------------------------------

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            str,
        ):
            return value

        if isinstance(
            value,
            int,
        ) and not isinstance(
            value,
            bool,
        ):
            return value

        # --------------------------------------------------------------
        # Floating-point values
        # --------------------------------------------------------------

        if isinstance(
            value,
            float,
        ):
            if math.isfinite(
                value
            ):
                return value

            # NaN / +inf / -inf
            return None

        # --------------------------------------------------------------
        # Enum
        # --------------------------------------------------------------

        if isinstance(
            value,
            Enum,
        ):
            return cls._sanitize_value(
                value.value,
                _seen=_seen,
            )

        # --------------------------------------------------------------
        # UUID
        # --------------------------------------------------------------

        if isinstance(
            value,
            UUID,
        ):
            return str(value)

        # --------------------------------------------------------------
        # Datetime
        # --------------------------------------------------------------

        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        # --------------------------------------------------------------
        # Date
        # --------------------------------------------------------------

        if isinstance(
            value,
            date,
        ):
            return value.isoformat()

        # --------------------------------------------------------------
        # Time
        # --------------------------------------------------------------

        if isinstance(
            value,
            time,
        ):
            return value.isoformat()

        # --------------------------------------------------------------
        # Decimal
        # --------------------------------------------------------------

        if isinstance(
            value,
            Decimal,
        ):
            try:
                float_value = float(
                    value
                )
            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                return None

            if not math.isfinite(
                float_value
            ):
                return None

            return float_value

        # --------------------------------------------------------------
        # Recursion protection.
        #
        # Only container/object values need tracking.
        # --------------------------------------------------------------

        is_container = isinstance(
            value,
            (
                dict,
                list,
                tuple,
                set,
                frozenset,
            ),
        )

        if is_container:
            object_id = id(value)

            if object_id in _seen:
                logger.warning(
                    "Circular reference detected while sanitizing "
                    "AgentResult value. Replacing with None."
                )
                return None

            _seen.add(
                object_id
            )

        try:
            # ----------------------------------------------------------
            # Dictionary
            # ----------------------------------------------------------

            if isinstance(
                value,
                dict,
            ):
                result: dict[str, Any] = {}

                for key, item in value.items():
                    normalized_key = cls._normalize_dict_key(
                        key
                    )

                    result[normalized_key] = (
                        cls._sanitize_value(
                            item,
                            _seen=_seen,
                        )
                    )

                return result

            # ----------------------------------------------------------
            # List
            # ----------------------------------------------------------

            if isinstance(
                value,
                list,
            ):
                return [
                    cls._sanitize_value(
                        item,
                        _seen=_seen,
                    )
                    for item in value
                ]

            # ----------------------------------------------------------
            # Tuple
            # ----------------------------------------------------------

            if isinstance(
                value,
                tuple,
            ):
                return [
                    cls._sanitize_value(
                        item,
                        _seen=_seen,
                    )
                    for item in value
                ]

            # ----------------------------------------------------------
            # Set / frozenset
            # ----------------------------------------------------------

            if isinstance(
                value,
                (
                    set,
                    frozenset,
                ),
            ):
                return [
                    cls._sanitize_value(
                        item,
                        _seen=_seen,
                    )
                    for item in value
                ]

            # ----------------------------------------------------------
            # numpy / pandas compatibility
            #
            # We intentionally do not import numpy or pandas here.
            # AgentResult should not have hard dependencies on them.
            #
            # Many numpy/pandas objects expose:
            #
            #     .item()
            #
            # or:
            #
            #     .tolist()
            #
            # Use those protocols defensively.
            # ----------------------------------------------------------

            item_method = getattr(
                value,
                "item",
                None,
            )

            if callable(
                item_method
            ):
                try:
                    converted = item_method()

                    # Avoid infinite recursion if .item() returns
                    # the object itself.
                    if converted is not value:
                        return cls._sanitize_value(
                            converted,
                            _seen=_seen,
                        )

                except Exception:
                    pass

            # ----------------------------------------------------------
            # numpy arrays / pandas Series / similar objects
            # ----------------------------------------------------------

            tolist_method = getattr(
                value,
                "tolist",
                None,
            )

            if callable(
                tolist_method
            ):
                try:
                    converted = tolist_method()

                    if converted is not value:
                        return cls._sanitize_value(
                            converted,
                            _seen=_seen,
                        )

                except Exception:
                    pass

            # ----------------------------------------------------------
            # pandas.NA / pandas.NaT and similar missing-value
            # objects.
            #
            # We avoid importing pandas/numpy here.
            # ----------------------------------------------------------

            class_name = type(
                value
            ).__name__

            module_name = type(
                value
            ).__module__

            if (
                class_name in {
                    "NAType",
                    "NaTType",
                }
                or module_name.startswith(
                    "pandas"
                )
                and class_name in {
                    "NAType",
                    "NaTType",
                }
            ):
                return None

            # ----------------------------------------------------------
            # Generic numeric objects.
            #
            # Some numpy scalar types may not have been handled by
            # .item() above. Check whether the object behaves like a
            # real number.
            # ----------------------------------------------------------

            try:
                real_value = float(
                    value
                )

                if isinstance(
                    value,
                    complex,
                ):
                    return str(value)

                if math.isfinite(
                    real_value
                ):
                    # Preserve integer-like values where possible.
                    if (
                        hasattr(
                            value,
                            "dtype",
                        )
                        and str(
                            getattr(
                                value,
                                "dtype",
                                "",
                            )
                        ).startswith(
                            "int"
                        )
                    ):
                        try:
                            return int(
                                value
                            )
                        except Exception:
                            pass

                    return real_value

                return None

            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                pass

            # ----------------------------------------------------------
            # Generic object with __dict__
            # ----------------------------------------------------------

            object_dict = getattr(
                value,
                "__dict__",
                None,
            )

            if isinstance(
                object_dict,
                dict,
            ):
                return cls._sanitize_dict(
                    object_dict,
                    _seen=_seen,
                )

            # ----------------------------------------------------------
            # Last-resort string representation.
            #
            # This prevents arbitrary provider objects from leaking
            # through the JSON boundary.
            # ----------------------------------------------------------

            try:
                return str(
                    value
                )
            except Exception:
                return None

        finally:
            if is_container:
                _seen.discard(
                    id(value)
                )

    # ==================================================================
    # Dictionary Sanitization
    # ==================================================================

    @classmethod
    def _sanitize_dict(
        cls,
        value: dict[Any, Any],
        *,
        _seen: set[int] | None = None,
    ) -> dict[str, Any]:
        """
        Recursively sanitize a dictionary.

        Dictionary keys are converted to strings because JSON object
        keys must be strings.
        """

        if not isinstance(
            value,
            dict,
        ):
            return {}

        if _seen is None:
            _seen = set()

        object_id = id(
            value
        )

        if object_id in _seen:
            logger.warning(
                "Circular dictionary detected while sanitizing "
                "AgentResult."
            )
            return {}

        _seen.add(
            object_id
        )

        try:
            result: dict[str, Any] = {}

            for key, item in value.items():
                normalized_key = cls._normalize_dict_key(
                    key
                )

                result[normalized_key] = (
                    cls._sanitize_value(
                        item,
                        _seen=_seen,
                    )
                )

            return result

        finally:
            _seen.discard(
                object_id
            )

    # ==================================================================
    # List Sanitization
    # ==================================================================

    @classmethod
    def _sanitize_list(
        cls,
        value: Any,
    ) -> list[Any]:
        """
        Recursively sanitize list-like values.

        Invalid/non-list values become an empty list.

        Tuple, set, numpy-array, and pandas-series-like values are
        also supported through the generic sanitizer.
        """

        if value is None:
            return []

        sanitized = cls._sanitize_value(
            value
        )

        if isinstance(
            sanitized,
            list,
        ):
            return sanitized

        return []

    # ==================================================================
    # Dictionary Key Normalization
    # ==================================================================

    @classmethod
    def _normalize_dict_key(
        cls,
        key: Any,
    ) -> str:
        """
        Convert arbitrary dictionary keys into JSON-safe strings.
        """

        if isinstance(
            key,
            str,
        ):
            return key

        if isinstance(
            key,
            Enum,
        ):
            return str(
                key.value
            )

        if isinstance(
            key,
            UUID,
        ):
            return str(
                key
            )

        if isinstance(
            key,
            (
                datetime,
                date,
                time,
            ),
        ):
            return key.isoformat()

        if key is None:
            return "null"

        try:
            return str(
                key
            )
        except Exception:
            return "<unserializable-key>"

    # ==================================================================
    # Optional String Normalization
    # ==================================================================

    @staticmethod
    def _normalize_optional_string(
        value: Any,
    ) -> str | None:
        """
        Normalize an optional string field.

        None remains None.

        Other values are converted to strings so that fields such as
        task_id remain JSON-safe.
        """

        if value is None:
            return None

        if isinstance(
            value,
            str,
        ):
            return value

        return str(
            value
        )

    # ==================================================================
    # Source Normalization
    # ==================================================================

    @classmethod
    def _normalize_sources(
        cls,
        sources: Any,
    ) -> list[str]:
        """
        Normalize sources into a unique list of strings.

        Non-JSON-safe source values are converted to strings.
        """

        if sources is None:
            return []

        if isinstance(
            sources,
            (
                list,
                tuple,
                set,
                frozenset,
            ),
        ):
            values = list(
                sources
            )
        else:
            values = [
                sources
            ]

        normalized: list[str] = []

        for source in values:
            if source is None:
                continue

            sanitized = cls._sanitize_value(
                source
            )

            if sanitized is None:
                continue

            if isinstance(
                sanitized,
                str,
            ):
                normalized_source = sanitized
            else:
                normalized_source = str(
                    sanitized
                )

            if normalized_source not in normalized:
                normalized.append(
                    normalized_source
                )

        return normalized

    # ==================================================================
    # Safe String Conversion
    # ==================================================================

    @staticmethod
    def _safe_string(
        value: Any,
    ) -> str:
        """
        Convert a value into a safe string.

        Used primarily for error messages.
        """

        if value is None:
            return "Unknown agent execution error."

        try:
            return str(
                value
            )
        except Exception:
            return "Unknown agent execution error."

    # ==================================================================
    # Representation
    # ==================================================================

    def __repr__(self) -> str:
        """
        Provide a concise debugging representation.
        """

        return (
            "AgentResult("
            f"agent_name={self.agent_name!r}, "
            f"status={self.status.value!r}, "
            f"task_id={self.task_id!r}, "
            f"confidence={self.confidence!r}, "
            f"findings={len(self.findings)}, "
            f"evidence={len(self.evidence)}, "
            f"citations={len(self.citations)}, "
            f"error={self.error!r}"
            ")"
        )