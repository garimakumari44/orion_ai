# models/ranking.py

from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field



class RankingScore(BaseModel):
    """
    Individual ranking components.
    """

    relevance: float = 0.0

    semantic_score: float = 0.0

    freshness_score: float = 0.0

    authority_score: float = 0.0

    diversity_score: float = 0.0



class RankedDocument(BaseModel):
    """
    Document after reranking.
    """

    id: UUID = Field(
        default_factory=uuid4
    )


    document_id: str


    chunk_id: Optional[str] = None


    content: str


    original_rank: Optional[int] = None


    final_rank: int


    score: float


    ranking_score: RankingScore


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )



class RankingRequest(BaseModel):
    """
    Ranking pipeline input.
    """

    query: str


    documents: List[str]


    strategy: str = (
        "cross_encoder"
    )


    top_k: int = 10



class RankingResponse(BaseModel):
    """
    Ranking pipeline output.
    """

    query: str


    results: List[RankedDocument] = Field(
        default_factory=list
    )


    model: Optional[str] = None


    latency_ms: Optional[float] = None


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )