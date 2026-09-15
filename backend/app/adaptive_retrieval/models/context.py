from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ContextChunk(BaseModel):
    """
    Individual chunk inside LLM context.
    """

    id: UUID = Field(
        default_factory=uuid4
    )

    document_id: str

    content: str

    citation: Optional[str] = None

    relevance_score: float = 0.0

    token_count: Optional[int] = None



class RetrievalContext(BaseModel):
    """
    Runtime retrieval context.

    Holds query, retrieved chunks,
    metadata and execution information.
    """

    id: UUID = Field(
        default_factory=uuid4
    )

    query: str

    chunks: List[ContextChunk] = Field(
        default_factory=list
    )

    total_tokens: int = 0

    max_tokens: int = 4000

    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )



class ContextWindow(BaseModel):
    """
    Complete context supplied to LLM.
    """

    id: UUID = Field(
        default_factory=uuid4
    )

    query: str

    chunks: List[ContextChunk] = Field(
        default_factory=list
    )

    total_tokens: int = 0

    max_tokens: int = 4000



class ContextRequest(BaseModel):
    """
    Context builder input.
    """

    query: str

    ranked_documents: List[str]

    token_budget: int = 4000

    include_citations: bool = True



class ContextResponse(BaseModel):
    """
    Final generated context.
    """

    context: ContextWindow

    formatted_prompt: Optional[str] = None

    compression_applied: bool = False

    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )