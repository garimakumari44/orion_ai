"""
Evidence Matching

Matches extracted claims against retrieved evidence and determines
whether the evidence supports, contradicts, or is unrelated.

Works with:
- Claim extraction
- Retrieved documents
- Citation verification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class EvidenceLabel(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    PARTIAL = "partial"
    IRRELEVANT = "irrelevant"
    UNKNOWN = "unknown"


@dataclass
class Evidence:

    id: str
    text: str
    source: str
    score: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class EvidenceMatch:

    claim: str
    evidence: Evidence
    similarity: float
    label: EvidenceLabel
    confidence: float


class EvidenceMatcher:
    """
    Matches claims with evidence.

    Current implementation:
        keyword overlap

    Can later be upgraded to:
        • Embedding similarity
        • Cross-Encoder
        • LLM Judge
    """

    def __init__(self, threshold: float = 0.35):
        self.threshold = threshold

    # ---------------------------------------------------------

    @staticmethod
    def _tokenize(text: str):

        return set(
            word.lower().strip(".,!?;:()[]{}")
            for word in text.split()
            if word.strip()
        )

    # ---------------------------------------------------------

    def similarity(self, claim: str, evidence: str) -> float:

        a = self._tokenize(claim)
        b = self._tokenize(evidence)

        if not a or not b:
            return 0.0

        overlap = len(a & b)
        union = len(a | b)

        return overlap / union

    # ---------------------------------------------------------

    def classify(
        self,
        similarity: float,
    ) -> EvidenceLabel:

        if similarity >= 0.75:
            return EvidenceLabel.SUPPORTS

        if similarity >= 0.45:
            return EvidenceLabel.PARTIAL

        if similarity >= self.threshold:
            return EvidenceLabel.IRRELEVANT

        return EvidenceLabel.UNKNOWN

    # ---------------------------------------------------------

    def match(
        self,
        claim: str,
        evidences: List[Evidence],
    ) -> List[EvidenceMatch]:

        matches = []

        for evidence in evidences:

            sim = self.similarity(claim, evidence.text)

            label = self.classify(sim)

            matches.append(
                EvidenceMatch(
                    claim=claim,
                    evidence=evidence,
                    similarity=sim,
                    label=label,
                    confidence=sim,
                )
            )

        matches.sort(
            key=lambda x: x.similarity,
            reverse=True,
        )

        return matches

    # ---------------------------------------------------------

    def best_match(
        self,
        claim: str,
        evidences: List[Evidence],
    ) -> Optional[EvidenceMatch]:

        matches = self.match(claim, evidences)

        return matches[0] if matches else None