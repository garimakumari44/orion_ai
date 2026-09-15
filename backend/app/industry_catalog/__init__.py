"""
Industry Catalog.

Provides canonical industry resolution for the application.
"""

from .manager import IndustryCatalogManager
from .models import IndustryResult
from .resolver import IndustryResolver

__all__ = [
    "IndustryCatalogManager",
    "IndustryResolver",
    "IndustryResult",
]