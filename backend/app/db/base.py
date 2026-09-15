"""
app/db/base.py

Central SQLAlchemy model registry.

All ORM models must be imported here so that they are registered
with Base.metadata and discovered by Alembic.
"""

from app.db.database import Base

# Core models
from app.db.models.user import Users
from app.db.models.company import Company

# Industry catalog
from app.db.models.industry import Industry
from app.db.models.industry_metadata import IndustryMetadata
from app.db.models.industry_classification_source import (
    IndustryClassificationSource,
)

# Research
from app.db.models.research import Research
from app.db.models.research_execution import ResearchExecution
from app.db.models.research_result import ResearchResult



__all__ = [
    "Base",
    "Users",
    "Company",
    "Industry",
    "IndustryMetadata",
    "IndustryClassificationSource",
    "Research",
    "ResearchExecution",
    "ResearchResult",
    
]