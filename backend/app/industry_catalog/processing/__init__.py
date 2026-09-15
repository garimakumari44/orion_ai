"""
app/industry_catalog/processing

Industry catalog processing pipeline.

This package is responsible for converting raw industry
provider data into a canonical, validated, resolved,
confidence-scored industry record.

Processing is deterministic.

AI/research agents do NOT belong here.
"""

from .pipeline import IndustryProcessingPipeline
from .normalizer import IndustryNormalizer
from .validator import IndustryValidator
from .resolver import IndustryResolver
from .confidence import IndustryConfidenceCalculator

__all__ = [
    "IndustryProcessingPipeline",
    "IndustryNormalizer",
    "IndustryValidator",
    "IndustryResolver",
    "IndustryConfidenceCalculator",
]