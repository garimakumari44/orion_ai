# models/retrieval.py

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RetrievalDocument(BaseModel):
    """
    A single retrieved document/chunk.
    """

    id: UUID = Field(
        default_factory=uuid4
    )

    document_id: str

    chunk_id: Optional[str] = None


    content: str


    source: Optional[str] = None


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


    # Retrieval scores

    vector_score: Optional[float] = None

    keyword_score: Optional[float] = None

    graph_score: Optional[float] = None



class RetrievalRequest(BaseModel):
    """
    Request sent to retrieval engines.
    """

    query: str


    top_k: int = Field(
        default=10,
        ge=1,
        le=100
    )


    strategy: str = Field(
        default="hybrid"
    )


    filters: Dict[str, Any] = Field(
        default_factory=dict
    )


    enable_graph: bool = False



class RetrievalResponse(BaseModel):
    """
    Output from retrieval layer.
    """

    query: str


    documents: List[RetrievalDocument] = Field(
        default_factory=list
    )


    retriever: str


    total_results: int = 0


    latency_ms: Optional[float] = None


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )