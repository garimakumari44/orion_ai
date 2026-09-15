"""
Source validation.

Checks whether retrieved documents are trustworthy enough to support
generated answers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------

@dataclass(slots=True)
class Source:

    id: str
    title: str

    url: Optional[str] = None
    publisher: Optional[str] = None

    author: Optional[str] = None

    retrieved_at: Optional[datetime] = None

    credibility: float = 1.0

    metadata: Dict = field(default_factory=dict)


@dataclass(slots=True)
class SourceIssue:

    source_id: str
    message: str
    severity: str = "warning"


@dataclass(slots=True)
class SourceValidationResult:

    valid: bool

    issues: List[SourceIssue] = field(default_factory=list)

    trusted_sources: List[str] = field(default_factory=list)

    rejected_sources: List[str] = field(default_factory=list)

    @property
    def score(self) -> float:

        total = len(self.trusted_sources) + len(self.rejected_sources)

        if total == 0:
            return 0.0

        return len(self.trusted_sources) / total


# ---------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------

class SourceValidator:
    """
    Generic source quality validator.

    Trust score can come from:

    • search engine
    • retrieval engine
    • metadata
    • manual scoring
    """

    def __init__(
        self,
        minimum_credibility: float = 0.6,
    ):
        self.minimum_credibility = minimum_credibility

    def validate(
        self,
        sources: Iterable[Source],
    ) -> SourceValidationResult:

        trusted = []
        rejected = []
        issues = []

        for source in sources:

            ok = True

            if source.credibility < self.minimum_credibility:

                ok = False

                issues.append(
                    SourceIssue(
                        source.id,
                        f"Low credibility ({source.credibility:.2f})",
                        "warning",
                    )
                )

            if not source.title:

                ok = False

                issues.append(
                    SourceIssue(
                        source.id,
                        "Missing title",
                        "warning",
                    )
                )

            if ok:
                trusted.append(source.id)
            else:
                rejected.append(source.id)

        return SourceValidationResult(
            valid=len(rejected) == 0,
            issues=issues,
            trusted_sources=trusted,
            rejected_sources=rejected,
        )