"""
Verification Package

Provides tools for validating AI-generated responses through:
- Citation verification
- Source credibility checks
- URL validation
- Claim extraction
- Evidence matching
- Cross-source agreement analysis

This package is used by the Critic Engine to evaluate
factual reliability and grounding quality.
"""

from .citations import CitationVerifier
from .sources import SourceValidator
from .urls import URLVerifier
from .claims import ClaimExtractor
from .evidence import EvidenceMatcher
from .cross_reference import CrossReferenceAnalyzer


__all__ = [
    "CitationVerifier",
    "SourceValidator",
    "URLVerifier",
    "ClaimExtractor",
    "EvidenceMatcher",
    "CrossReferenceAnalyzer",
]


__version__ = "1.0.0"