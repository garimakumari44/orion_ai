# models/strategy.py

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field



class RetrievalStrategyType(str, Enum):
    """
    Available retrieval strategies.
    """

    DENSE = "dense"

    SPARSE = "sparse"

    HYBRID = "hybrid"

    GRAPH = "graph"

    MULTI_SOURCE = "multi_source"

    TEMPORAL = "temporal"

    MEMORY = "memory"

    AGENTIC = "agentic"



class RankingStrategyType(str, Enum):
    """
    Ranking approaches.
    """

    NONE = "none"

    BM25 = "bm25"

    CROSS_ENCODER = "cross_encoder"

    LLM_RERANK = "llm_rerank"

    FUSION = "fusion"



class ContextStrategyType(str, Enum):
    """
    Context construction strategies.
    """

    SIMPLE = "simple"

    COMPRESSED = "compressed"

    HIERARCHICAL = "hierarchical"

    CITATION_AWARE = "citation_aware"



class RetrievalStrategy(BaseModel):
    """
    Complete retrieval strategy configuration.

    Created by strategy selector and consumed
    by retrieval planner.
    """

    id: UUID = Field(
        default_factory=uuid4
    )


    name: str


    retrieval_type: RetrievalStrategyType = (
        RetrievalStrategyType.HYBRID
    )


    ranking_type: RankingStrategyType = (
        RankingStrategyType.CROSS_ENCODER
    )


    context_type: ContextStrategyType = (
        ContextStrategyType.CITATION_AWARE
    )


    # Retrieval parameters

    top_k: int = Field(
        default=10,
        ge=1,
        le=100
    )


    rerank_top_k: int = Field(
        default=5,
        ge=1
    )


    enable_graph_search: bool = False


    enable_memory_search: bool = False


    enable_query_expansion: bool = False



    # Model configuration

    embedding_model: Optional[str] = None

    reranker_model: Optional[str] = None

    llm_model: Optional[str] = None



    # Dynamic parameters

    parameters: Dict[str, Any] = Field(
        default_factory=dict
    )



class StrategyDecision(BaseModel):
    """
    Output from strategy selector.

    Explains why a strategy was selected.
    """

    query: str


    selected_strategy: RetrievalStrategy


    confidence: float = Field(
        default=0.0,
        ge=0,
        le=1
    )


    reasoning: Optional[str] = None


    alternatives: List[str] = Field(
        default_factory=list
    )


    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )



class StrategyRequest(BaseModel):
    """
    Input for strategy selection.
    """

    query: str


    intent: Optional[str] = None


    complexity: Optional[str] = None


    domain: Optional[str] = None


    constraints: Dict[str, Any] = Field(
        default_factory=dict
    )



class StrategyResponse(BaseModel):
    """
    API response for strategy selection.
    """

    strategy: RetrievalStrategy


    confidence: float


    explanation: Optional[str] = None


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )