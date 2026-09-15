"""
Research Intelligence Builder

High-level orchestration pipeline for
Multi-Agent AI Analyst Knowledge System.

Pipeline:

Sources
|
v
Connector Layer
|
v
Ingestion
|
v
Document Processing
|
v
Financial Knowledge Extraction
|
v
Entity + Relationship Graph
|
v
Research Memory
|
v
Embedding Generation
|
v
Storage
|
v
Hybrid Indexing
"""

from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime


# Connectors
from app.knowledge_system.connectors.manager import (
    ConnectorManager
)

# Ingestion
from app.knowledge_system.ingestion.manager import (
    IngestionManager
)

from app.knowledge_system.ingestion.pipeline import (
    ProcessingPipeline
)


# Enrichment
from app.knowledge_system.enrichment.manager import (
    EnrichmentManager
)


# Storage
from app.knowledge_system.storage.manager import (
    StorageManager
)


# Indexing
from app.knowledge_system.indexing.manager import (
    IndexManager
)


class KnowledgeBuilder:
    """
    Builds Research Intelligence Knowledge Base.

    Used by:

    - Fundamental Agent
    - Valuation Agent
    - Macro Agent
    - Risk Agent
    - Investment Committee Agent


    Responsibilities:

    1. Collect research sources
    2. Process documents
    3. Extract financial intelligence
    4. Build company knowledge graph
    5. Store analyst memory
    6. Create retrieval indexes

    """


    def __init__(
        self,

        connectors: ConnectorManager | None = None,

        ingestion: IngestionManager | None = None,

        enrichment: EnrichmentManager | None = None,

        pipeline: ProcessingPipeline | None = None,

        storage: StorageManager | None = None,

        indexing: IndexManager | None = None,

    ):

        self.connectors = (
            connectors
            or ConnectorManager()
        )


        self.ingestion = (
            ingestion
            or IngestionManager()
        )


        self.enrichment = (
            enrichment
            or EnrichmentManager()
        )


        self.pipeline = (
            pipeline
            or ProcessingPipeline()
        )


        self.storage = (
            storage
            or StorageManager()
        )


        self.indexing = (
            indexing
            or IndexManager()
        )


        #
        # Enrichment Services
        #
        # Expected from EnrichmentManager:
        #
        # graph
        # memory
        # extraction
        #

        self.graph = getattr(
            self.enrichment,
            "graph",
            None
        )


        self.memory = getattr(
            self.enrichment,
            "memory",
            None
        )


        self.extraction = getattr(
            self.enrichment,
            "extraction",
            None
        )



    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    async def initialize(self):
        """
        Initialize all knowledge services.
        """


        if hasattr(
            self.connectors,
            "initialize"
        ):
            await self.connectors.initialize()



        if hasattr(
            self.ingestion,
            "initialize"
        ):
            await self.ingestion.initialize()



        if self.enrichment:

            await self.enrichment.initialize()



        if hasattr(
            self.storage,
            "initialize"
        ):
            await self.storage.initialize()



        if hasattr(
            self.indexing,
            "initialize"
        ):
            await self.indexing.initialize()




    async def shutdown(self):
        """
        Shutdown knowledge services.
        """


        if hasattr(
            self.connectors,
            "shutdown"
        ):
            await self.connectors.shutdown()



        if hasattr(
            self.ingestion,
            "shutdown"
        ):
            await self.ingestion.shutdown()



        if self.enrichment:

            await self.enrichment.shutdown()



        if hasattr(
            self.storage,
            "close"
        ):
            await self.storage.close()



        if hasattr(
            self.indexing,
            "shutdown"
        ):
            await self.indexing.shutdown()




    # -------------------------------------------------
    # Company Research Builder
    # -------------------------------------------------

    async def build_company_research(
        self,
        company: str,
        connector_name: str,
        config: Any,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Build complete intelligence
        for one company.
        """


        connector = self.connectors.create(
            connector_name,
            config,
        )


        await connector.connect()


        try:

            # ---------------------------------
            # 1. Collect Documents
            # ---------------------------------

            raw_documents = await connector.fetch(
                company=company,
                **kwargs,
            )



            # ---------------------------------
            # 2. Ingestion
            # ---------------------------------

            documents = self.ingestion.ingest(
                raw_documents
            )


            processed_documents = []

            knowledge_objects = []



            for document in documents:


                # Document Processing

                processed = await self.pipeline.process(
                    document
                )


                processed_documents.append(
                    processed
                )



                # Financial Extraction

                if self.extraction:

                    knowledge = await self.extraction.extract(
                        processed
                    )

                else:

                    knowledge = processed



                knowledge_objects.append(
                    knowledge
                )



                # Knowledge Graph

                if self.graph and hasattr(
                    knowledge,
                    "nodes"
                ):

                    await self.graph.update(

                        company=company,

                        nodes=knowledge.nodes,

                        relations=knowledge.relations,

                    )



                # Research Memory

                if self.memory:

                    await self.memory.store(

                        company=company,

                        knowledge=knowledge,

                        timestamp=datetime.utcnow(),

                    )



                # Document Storage

                await self.storage.document_store.save(

                    document_id=processed["id"],

                    content=processed.get(
                        "content",
                        ""
                    ),

                    metadata={

                        **processed,

                        "company": company,

                    },

                )



            # ---------------------------------
            # 3. Indexing
            # ---------------------------------

            index_result = await self.indexing.index(
                processed_documents
            )



            return {

                "company": company,

                "documents_processed":
                    len(processed_documents),

                "knowledge_objects":
                    len(knowledge_objects),

                "graph_updated":
                    self.graph is not None,

                "indexed":
                    index_result,

                "timestamp":
                    datetime.utcnow(),

            }



        finally:

            await connector.disconnect()




    # -------------------------------------------------
    # Generic Connector Builder
    # -------------------------------------------------

    async def build_from_connector(
        self,
        connector_name: str,
        config: Any,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Generic knowledge ingestion.
        """


        connector = self.connectors.create(
            connector_name,
            config,
        )


        await connector.connect()



        try:


            raw_documents = await connector.fetch(
                **kwargs
            )


            documents = self.ingestion.ingest(
                raw_documents
            )


            results = []



            for document in documents:


                processed = await self.pipeline.process(
                    document
                )


                if self.extraction:

                    knowledge = await self.extraction.extract(
                        processed
                    )

                else:

                    knowledge = processed



                if self.graph and hasattr(
                    knowledge,
                    "nodes"
                ):

                    await self.graph.update(

                        nodes=knowledge.nodes,

                        relations=knowledge.relations,

                    )



                if self.memory:

                    await self.memory.store(
                        knowledge=knowledge
                    )



                results.append(
                    processed
                )



            await self.indexing.index(
                results
            )


            return results



        finally:

            await connector.disconnect()