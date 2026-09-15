"""
End-to-End tests for KnowledgeBuilder.

Pipeline tested:

Connector
    |
    v
Ingestion
    |
    v
Storage
    |
    v
Indexing
"""

from __future__ import annotations

import pytest

from app.knowledge_system.knowledge_builder import KnowledgeBuilder

from app.knowledge_system.connectors.base import (
    BaseConnector,
    ConnectorConfig,
)

from app.knowledge_system.connectors.manager import ConnectorManager

from app.knowledge_system.storage.manager import StorageManager

from app.knowledge_system.storage.stores.document_store import (
    InMemoryDocumentStore,
)

from app.knowledge_system.indexing.manager import IndexManager


# ---------------------------------------------------------
# Fake connector for testing
# ---------------------------------------------------------

class MockConnector(BaseConnector):

    @property
    def source_type(self) -> str:
        return "mock"


    async def connect(self):

        self.connected = True


    async def disconnect(self):

        self.connected = False


    async def fetch(self, **kwargs):

        return [
            {
                "id": "doc-1",
                "title": "Test Knowledge Document",
                "content": "This is a knowledge system test document.",
                "source": "mock",
            }
        ]



# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture
def connector_manager():

    manager = ConnectorManager()

    manager.register(
        "mock",
        MockConnector,
    )

    return manager



@pytest.fixture
def storage_manager():

    return StorageManager(
        document_store=InMemoryDocumentStore()
    )



@pytest.fixture
def builder(
    connector_manager,
    storage_manager,
):

    return KnowledgeBuilder(
        connectors=connector_manager,
        storage=storage_manager,
        indexing=IndexManager(),
    )



# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_initialize_knowledge_builder(
    builder,
):

    await builder.initialize()

    assert builder.connectors is not None
    assert builder.storage is not None
    assert builder.indexing is not None

    await builder.shutdown()



@pytest.mark.asyncio
async def test_build_knowledge_base_from_connector(
    builder,
):

    await builder.initialize()


    config = ConnectorConfig(
        name="mock"
    )


    result = await builder.build_from_connector(
        connector_name="mock",
        config=config,
    )


    assert len(result) == 1

    assert result[0]["id"] == "doc-1"

    assert result[0]["title"] == (
        "Test Knowledge Document"
    )


    await builder.shutdown()



@pytest.mark.asyncio
async def test_document_saved_to_storage(
    builder,
):

    await builder.initialize()


    config = ConnectorConfig(
        name="mock"
    )


    await builder.build_from_connector(
        "mock",
        config,
    )


    stored = await (
        builder
        .storage
        .document_store
        .get("doc-1")
    )


    assert stored is not None

    assert stored["id"] == "doc-1"

    assert (
        stored["content"]
        ==
        "This is a knowledge system test document."
    )


    await builder.shutdown()



@pytest.mark.asyncio
async def test_unknown_connector_fails(
    builder,
):

    await builder.initialize()


    config = ConnectorConfig(
        name="unknown"
    )


    with pytest.raises(ValueError):

        await builder.build_from_connector(
            "unknown",
            config,
        )


    await builder.shutdown()