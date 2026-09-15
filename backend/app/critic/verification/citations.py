"""
Citation verification.

Responsible for validating citations attached to model responses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------

@dataclass(slots=True)
class Citation:

    id: str
    source_id: str
    span: str
    start: int
    end: int


@dataclass(slots=True)
class CitationIssue:

    citation_id: str
    message: str
    severity: str = "warning"


@dataclass(slots=True)
class CitationVerificationResult:

    valid: bool
    citations: List[Citation] = field(default_factory=list)
    issues: List[CitationIssue] = field(default_factory=list)

    @property
    def score(self) -> float:
        if not self.citations:
            return 0.0

        failures = len(self.issues)
        return max(0.0, 1.0 - failures / len(self.citations))


# ---------------------------------------------------------------------
# Citation verifier
# ---------------------------------------------------------------------

class CitationVerifier:
    """
    Verifies citation syntax and references.

    Supported examples:

    [1]
    [2]
    (Source: doc_12)
    """

    NUMBER_PATTERN = re.compile(r"\[(\d+)]")
    SOURCE_PATTERN = re.compile(r"\(Source:\s*([^)]+)\)")

    def extract(self, text: str) -> List[Citation]:

        citations: List[Citation] = []

        for match in self.NUMBER_PATTERN.finditer(text):
            cid = match.group(1)

            citations.append(
                Citation(
                    id=cid,
                    source_id=cid,
                    span=match.group(0),
                    start=match.start(),
                    end=match.end(),
                )
            )

        for match in self.SOURCE_PATTERN.finditer(text):
            sid = match.group(1).strip()

            citations.append(
                Citation(
                    id=sid,
                    source_id=sid,
                    span=match.group(0),
                    start=match.start(),
                    end=match.end(),
                )
            )

        return citations

    def verify(
        self,
        text: str,
        available_sources: Optional[Dict[str, object]] = None,
    ) -> CitationVerificationResult:

        citations = self.extract(text)

        issues: List[CitationIssue] = []

        source_ids = set(available_sources or {})

        for citation in citations:

            if available_sources is not None:
                if citation.source_id not in source_ids:
                    issues.append(
                        CitationIssue(
                            citation.id,
                            f"Unknown source '{citation.source_id}'",
                            "error",
                        )
                    )

        return CitationVerificationResult(
            valid=len(issues) == 0,
            citations=citations,
            issues=issues,
        )