"""
Shared enumerations for the Knowledge System.
"""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """
    Base enum whose values are strings.
    """

    def __str__(self) -> str:
        return self.value


# ============================================================================
# Document
# ============================================================================

class DocumentType(StrEnum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    EMAIL = "email"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    WEBPAGE = "webpage"
    GITHUB = "github"
    GITLAB = "gitlab"
    NOTION = "notion"
    CONFLUENCE = "confluence"
    JIRA = "jira"
    SLACK = "slack"
    DATABASE = "database"
    API = "api"
    OTHER = "other"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ============================================================================
# Chunk
# ============================================================================

class ChunkType(StrEnum):
    TEXT = "text"
    CODE = "code"
    TABLE = "table"
    IMAGE = "image"
    HEADER = "header"
    FOOTER = "footer"
    METADATA = "metadata"


# ============================================================================
# Embeddings
# ============================================================================

class EmbeddingProvider(StrEnum):
    OPENAI = "openai"
    COHERE = "cohere"
    VOYAGE = "voyage"
    HUGGINGFACE = "huggingface"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    BGE = "bge"
    E5 = "e5"
    JINA = "jina"
    CUSTOM = "custom"


# ============================================================================
# Entity Extraction
# ============================================================================

class EntityType(StrEnum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    PRODUCT = "product"
    EVENT = "event"
    DATE = "date"
    TIME = "time"
    MONEY = "money"
    PERCENT = "percent"
    LANGUAGE = "language"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"
    CUSTOM = "custom"


# ============================================================================
# Relationships
# ============================================================================

class RelationshipType(StrEnum):
    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    MENTIONS = "mentions"
    CITES = "cites"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    CALLS = "calls"


# ============================================================================
# Indexing
# ============================================================================

class IndexType(StrEnum):
    VECTOR = "vector"
    KEYWORD = "keyword"
    GRAPH = "graph"
    METADATA = "metadata"
    TEMPORAL = "temporal"
    HYBRID = "hybrid"


# ============================================================================
# Retrieval
# ============================================================================

class RetrievalStrategy(StrEnum):
    VECTOR = "vector"
    BM25 = "bm25"
    HYBRID = "hybrid"
    GRAPH = "graph"
    METADATA = "metadata"
    TEMPORAL = "temporal"
    MULTI_STAGE = "multi_stage"


# ============================================================================
# Processing Pipeline
# ============================================================================

class ProcessingStage(StrEnum):
    INGESTION = "ingestion"
    CLEANING = "cleaning"
    NORMALIZATION = "normalization"
    SPLITTING = "splitting"
    ENRICHMENT = "enrichment"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    STORAGE = "storage"
    COMPLETED = "completed"


# ============================================================================
# Quality
# ============================================================================

class QualityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"


# ============================================================================
# Storage
# ============================================================================

class StorageBackend(StrEnum):
    POSTGRES = "postgres"
    QDRANT = "qdrant"
    NEO4J = "neo4j"
    ELASTICSEARCH = "elasticsearch"
    REDIS = "redis"
    MONGODB = "mongodb"
    FILESYSTEM = "filesystem"


# ============================================================================
# Connector
# ============================================================================

class ConnectorType(StrEnum):
    FILESYSTEM = "filesystem"
    GITHUB = "github"
    GITLAB = "gitlab"
    NOTION = "notion"
    CONFLUENCE = "confluence"
    JIRA = "jira"
    SLACK = "slack"
    API = "api"
    DATABASE = "database"
    WEB = "web"
    ARXIV = "arxiv"
    PAPERS = "papers"


# ============================================================================
# Search
# ============================================================================

class SearchMode(StrEnum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    GRAPH = "graph"
    RERANKED = "reranked"