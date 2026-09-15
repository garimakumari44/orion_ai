"""
Retrieval Request Models

Defines input schemas for the Adaptive Retrieval System.

A retrieval request contains:
- user query
- optional user/session information
- retrieval preferences
- constraints
- metadata
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    """
    Input request for adaptive retrieval pipeline.

    Flow:

    User Query
        ↓
    Query Analyzer
        ↓
    Query Rewriter
        ↓
    Retrieval Planner
        ↓
    Retriever Manager
        ↓
    Ranking
        ↓
    Context Builder
    """

    # --------------------------------------------------
    # Request Identity
    # --------------------------------------------------

    request_id: UUID = Field(
        default_factory=uuid4,
        description="Unique retrieval request identifier"
    )


    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Request creation timestamp"
    )


    # --------------------------------------------------
    # Query
    # --------------------------------------------------

    query: str = Field(
        ...,
        min_length=1,
        description="User search/query text"
    )


    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation/session identifier"
    )


    user_id: Optional[str] = Field(
        default=None,
        description="User identifier"
    )


    # --------------------------------------------------
    # Retrieval Configuration
    # --------------------------------------------------

    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of documents to retrieve"
    )


    enable_reranking: bool = Field(
        default=True,
        description="Enable ranking stage"
    )


    enable_query_rewrite: bool = Field(
        default=True,
        description="Enable query rewriting"
    )


    enable_hyde: bool = Field(
        default=False,
        description="Enable HyDE hypothetical document generation"
    )


    # --------------------------------------------------
    # Retrieval Modes
    # --------------------------------------------------

    retrieval_modes: Optional[List[str]] = Field(
        default=None,
        description="""
        Retrieval strategies allowed.

        Examples:
        - dense
        - sparse
        - bm25
        - graph
        - memory
        """
    )


    # --------------------------------------------------
    # Filtering
    # --------------------------------------------------

    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata filters for retrieval"
    )


    namespaces: Optional[List[str]] = Field(
        default=None,
        description="Knowledge namespaces to search"
    )


    # --------------------------------------------------
    # Context
    # --------------------------------------------------

    previous_context: Optional[str] = Field(
        default=None,
        description="Previous conversation context"
    )


    max_context_tokens: int = Field(
        default=4000,
        ge=256,
        description="Maximum context size returned"
    )


    # --------------------------------------------------
    # Debug / Evaluation
    # --------------------------------------------------

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata"
    )


    debug: bool = Field(
        default=False,
        description="Enable debug tracing"
    )


    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain transformer architecture",
                "top_k": 5,
                "enable_query_rewrite": True,
                "enable_hyde": True,
                "retrieval_modes": [
                    "dense",
                    "bm25"
                ],
                "filters": {
                    "source": "research_papers"
                }
            }
        }