"""
Retrieval Response Models

Final output returned by
adaptive retrieval pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RetrievalResponse(BaseModel):
    """
    Response returned after retrieval.
    """


    query_id: Optional[str] = None


    success: bool = True


    answer_context: Optional[str] = None


    documents: List[Dict[str, Any]] = Field(
        default_factory=list
    )


    sources: List[str] = Field(
        default_factory=list
    )


    # Pipeline information

    retrievers_used: List[str] = Field(
        default_factory=list
    )


    latency_ms: float = 0.0


    token_usage: Dict[str, int] = Field(
        default_factory=dict
    )


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )