"""
Cross Source Verification

Checks whether multiple independent sources agree
on the same factual claim.

Future upgrades:
    • Knowledge Graph validation
    • Multi-hop reasoning
    • Consensus weighting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from .evidence import (
    Evidence,
    EvidenceMatcher,
)


class Consensus(str, Enum):
    VERIFIED = "verified"
    MOSTLY_VERIFIED = "mostly_verified"
    CONFLICTING = "conflicting"
    INSUFFICIENT = "insufficient"


@dataclass
class CrossReferenceResult:

    claim: str

    consensus: Consensus

    agreement_ratio: float

    supporting_sources: List[str] = field(default_factory=list)

    conflicting_sources: List[str] = field(default_factory=list)

    evidence: List[Evidence] = field(default_factory=list)


class CrossReferenceVerifier:

    def __init__(self):

        self.matcher = EvidenceMatcher()

    # -------------------------------------------------------

    def verify(
        self,
        claim: str,
        evidences: List[Evidence],
    ) -> CrossReferenceResult:

        matches = self.matcher.match(claim, evidences)

        supports = []
        conflicts = []

        for match in matches:

            if match.similarity >= 0.70:
                supports.append(match.evidence.source)

            elif match.similarity < 0.25:
                conflicts.append(match.evidence.source)

        total = len(evidences)

        agreement = (
            len(supports) / total
            if total
            else 0.0
        )

        if total == 0:
            consensus = Consensus.INSUFFICIENT

        elif agreement >= 0.80:
            consensus = Consensus.VERIFIED

        elif agreement >= 0.50:
            consensus = Consensus.MOSTLY_VERIFIED

        elif supports:
            consensus = Consensus.CONFLICTING

        else:
            consensus = Consensus.INSUFFICIENT

        return CrossReferenceResult(
            claim=claim,
            consensus=consensus,
            agreement_ratio=agreement,
            supporting_sources=supports,
            conflicting_sources=conflicts,
            evidence=evidences,
        )

    # -------------------------------------------------------

    def verify_many(
        self,
        claims: List[str],
        evidences: List[Evidence],
    ) -> List[CrossReferenceResult]:

        return [
            self.verify(claim, evidences)
            for claim in claims
        ]