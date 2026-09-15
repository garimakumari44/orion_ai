"""
planner/retrieval_planner.py

Adaptive Retrieval Planning Layer

Responsibilities
----------------
- Convert QueryAnalysis into RetrievalPlan
- Decide which retrievers should execute
- Configure retrieval strategy
- Enable reranking, expansion, compression
- Handle multi-hop, temporal, graph, code, and research queries

This layer does NOT perform NLP.
All query understanding comes from QueryAnalyzer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from .query_analyzer import QueryAnalysis
from .intent_classifier import RetrievalIntent


# ============================================================
# Retrieval Modes
# ============================================================


class RetrievalMode(str, Enum):

    NONE = "none"

    KEYWORD = "keyword"

    VECTOR = "vector"

    GRAPH = "graph"

    HYBRID = "hybrid"

    WEB = "web"

    MULTI_STAGE = "multi_stage"
    
    MEMORY = "memory"
    MEMORY_HYBRID = "memory_hybrid"


# ============================================================
# Retrieval Plan
# ============================================================


@dataclass(slots=True)
class RetrievalPlan:

    """
    Execution blueprint for RetrieverManager.
    """

    mode: RetrievalMode

    retrievers: List[str] = field(default_factory=list)

    top_k: int = 5

    rerank: bool = True
    compress_context: bool = False

    use_query_expansion: bool = False
    use_hyde: bool = False

    use_graph_expansion: bool = False

    # -----------------------------
    # Memory
    # -----------------------------

    use_memory: bool = False

    memory_types: List[str] = field(default_factory=list)

    memory_top_k: int = 5

    # -----------------------------
    # Web
    # -----------------------------

    use_web: bool = False

    # -----------------------------
    # Metadata filtering
    # -----------------------------

    use_metadata_filters: bool = False

    filters: Dict[str, Any] = field(default_factory=dict)

    # -----------------------------
    # Execution
    # -----------------------------

    retrieval_steps: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Retrieval Planner
# ============================================================


class RetrievalPlanner:
    """
    Creates retrieval execution plans.

    Input:
        QueryAnalysis

    Output:
        RetrievalPlan
    """


    def create_plan(
        self,
        analysis: QueryAnalysis,
    ) -> RetrievalPlan:


        intent = analysis.intent.primary


        # ----------------------------------------------------
        # Greeting / No retrieval
        # ----------------------------------------------------

        if intent == RetrievalIntent.UNKNOWN:

            return RetrievalPlan(
                mode=RetrievalMode.NONE,
                retrievers=[],
                rerank=False,
                retrieval_steps=[
                    "No Retrieval Required"
                ],
            )

        if self._should_use_memory(analysis):

         return RetrievalPlan(

            mode=RetrievalMode.MEMORY_HYBRID,

            retrievers=[
                "memory",
                "dense",
            ],

            top_k=8,

            memory_top_k=5,

            rerank=True,

            use_memory=True,

            memory_types=self._select_memory_types(analysis),

            retrieval_steps=[
                "Memory Retrieval",
                "Semantic Retrieval",
                "Merge",
                "Rerank",
            ],

            metadata={
                "reason": "Memory aware query"
            },
        )
        # ----------------------------------------------------
        # Temporal / Latest Information
        # ----------------------------------------------------

        if analysis.has_temporal_reference:


            return RetrievalPlan(

                mode=RetrievalMode.WEB,


                retrievers=[
                    "memory",
                    "web",
                    "dense",
                ],


                top_k=15,


                rerank=True,


                compress_context=True,


                use_web=True,
                memory_types=self._select_memory_types(analysis),


                retrieval_steps=[

                    "Recent Web Search",

                    "Vector Retrieval",

                    "Merge Results",

                    "Rerank",

                    "Context Compression",

                ],

                metadata={
                    "reason":
                    "Temporal query"
                }
            )


        # ----------------------------------------------------
        # Code Queries
        # ----------------------------------------------------

        if (
            intent == RetrievalIntent.PROCEDURE
            and self._contains_code_signal(
                analysis
            )
        ):


            return RetrievalPlan(

                mode=RetrievalMode.HYBRID,


                retrievers=[
                    "memory",

                    "dense",

                    "sparse",

                    "code",

                ],


                top_k=20,


                rerank=True,


                compress_context=True,


                use_query_expansion=True,

                use_memory=True,

                memory_types=self._select_memory_types(analysis),
                retrieval_steps=[

                    "Code Search",

                    "Vector Retrieval",

                    "Keyword Retrieval",

                    "Merge",

                    "Rerank",

                ],

                metadata={
                    "reason":
                    "Code generation task"
                }
            )


        # ----------------------------------------------------
        # Multi-hop reasoning
        # ----------------------------------------------------

        if analysis.complexity == "complex":


            return RetrievalPlan(

                mode=RetrievalMode.MULTI_STAGE,


                retrievers=[
                    "memory",
                    "dense",

                    "sparse",

                    "graph",

                ],
                use_memory=True,

                memory_types=self._select_memory_types(analysis),



                top_k=25,


                rerank=True,


                compress_context=True,


                use_query_expansion=True,


                use_graph_expansion=True,


                retrieval_steps=[

                    "Initial Retrieval",

                    "Graph Expansion",

                    "Keyword Retrieval",

                    "Merge",

                    "Rerank",

                    "Compress",

                ],

                metadata={
                    "reason":
                    "Complex reasoning query"
                }
            )


        # ----------------------------------------------------
        # Entity / Knowledge Graph Queries
        # ----------------------------------------------------

        if analysis.entities:


            return RetrievalPlan(

                mode=RetrievalMode.GRAPH,


                retrievers=[

                    "graph",

                    "dense",

                ],


                top_k=10,


                rerank=True,


                use_graph_expansion=True,


                use_metadata_filters=True,


                retrieval_steps=[

                    "Entity Resolution",

                    "Graph Traversal",

                    "Vector Retrieval",

                    "Rerank",

                ],

                metadata={
                    "entities":
                    analysis.entities
                }

            )


        # ----------------------------------------------------
        # Research / Explanation
        # ----------------------------------------------------

        if intent in [

            RetrievalIntent.EXPLANATION,

            RetrievalIntent.REASONING,

            RetrievalIntent.RESEARCH,

        ]:


            return RetrievalPlan(

                mode=RetrievalMode.HYBRID,


                retrievers=[

                    "dense",
                    "memory",

                    "sparse",

                ],
                use_memory=True,

                memory_types=self._select_memory_types(analysis),


                top_k=15,


                rerank=True,


                compress_context=True,


                use_query_expansion=True,


                use_hyde=True,


                retrieval_steps=[

                    "Query Expansion",

                    "Dense Retrieval",

                    "Sparse Retrieval",

                    "Merge",

                    "Rerank",

                    "Compress",

                ],

            )


        # ----------------------------------------------------
        # Comparison
        # ----------------------------------------------------

        if intent == RetrievalIntent.COMPARISON:


            return RetrievalPlan(

                mode=RetrievalMode.HYBRID,


                retrievers=[
                    "memory",
                    "dense",

                    "sparse",

                    "graph",

                ],

                use_memory=True,

                memory_types=self._select_memory_types(analysis),
                top_k=20,


                rerank=True,


                use_graph_expansion=True,


                retrieval_steps=[

                    "Retrieve Entities",

                    "Find Relationships",

                    "Hybrid Retrieval",

                    "Rerank",

                ],

            )


        # ----------------------------------------------------
        # Default
        # ----------------------------------------------------

        return RetrievalPlan(

            mode=RetrievalMode.VECTOR,


            retrievers=[
                "memory",
                "dense"

            ],
            use_memory=True,
            memory_types=self._select_memory_types(analysis),



            top_k=8,


            rerank=True,


            retrieval_steps=[

                "Embedding Retrieval",

                "Rerank",

            ],

            metadata={
                "reason":
                "Default semantic retrieval"
            }

        )


    # ========================================================
    # Helpers
    # ========================================================

    @staticmethod
    def _should_use_memory(
        analysis: QueryAnalysis,
    ) -> bool:
        """
        Decide whether the user's previous interactions or stored
        knowledge are likely to improve retrieval.
        """

        memory_terms = {
            "remember",
            "previous",
            "earlier",
            "before",
            "last",
            "continue",
            "again",
            "same",
            "project",
            "repository",
            "our",
            "my",
        }

        if any(token in memory_terms for token in analysis.tokens):
            return True

        if analysis.entities:
            return True

        if analysis.complexity == "complex":
            return True

        if analysis.has_temporal_reference:
            return True

        return False

    @staticmethod
    def _select_memory_types(
        analysis: QueryAnalysis,
    ) -> List[str]:
        """
        Determine which memory stores should be queried.
        """

        memory = ["working"]

        if analysis.complexity == "complex":
            memory.extend(["episodic", "semantic"])

        elif analysis.entities:
            memory.append("semantic")

        elif analysis.has_temporal_reference:
            memory.append("episodic")

        return list(dict.fromkeys(memory))
    @staticmethod
    def _contains_code_signal(
        analysis: QueryAnalysis
    ) -> bool:


        code_terms = {

            "python",

            "javascript",

            "typescript",

            "api",

            "function",

            "class",

            "implement",

            "build",

            "code",

            "debug",

        }


        return any(

            token in code_terms

            for token in analysis.tokens

        )