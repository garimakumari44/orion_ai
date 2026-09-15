from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KnowledgeSystemConfig(BaseSettings):
    """
    Configuration for the Knowledge System.
    """

    # -------------------------
    # General
    # -------------------------

    workspace_dir: Path = Field(default=Path("./workspace"))
    data_dir: Path = Field(default=Path("./data"))
    cache_dir: Path = Field(default=Path("./cache"))

    # -------------------------
    # Processing
    # -------------------------

    max_document_size_mb: int = 100
    chunk_size: int = 1024
    chunk_overlap: int = 200

    # -------------------------
    # Embeddings
    # -------------------------

    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-large"
    embedding_batch_size: int = 128

    # -------------------------
    # Vector Store
    # -------------------------

    vector_store: str = "qdrant"

    # -------------------------
    # Knowledge Graph
    # -------------------------

    graph_backend: str = "neo4j"

    # -------------------------
    # Metadata
    # -------------------------

    enable_versioning: bool = True
    enable_deduplication: bool = True

    model_config = SettingsConfigDict(
        env_prefix="KNOWLEDGE_",
        env_file=".env",
        extra="ignore",
    )


config = KnowledgeSystemConfig()