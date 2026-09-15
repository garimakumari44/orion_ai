import pytest

from app.knowledge_system.storage.manager import StorageManager
from app.knowledge_system.storage.transaction import StorageTransaction


# ---------------------------------------------------------
# Fake store for testing
# ---------------------------------------------------------

class FakeStore:

    def __init__(self, name="fake_store"):
        self.name = name
        self.initialized = False
        self.closed = False


    async def initialize(self):
        self.initialized = True


    async def close(self):
        self.closed = True


    async def health(self):
        return {
            "status": "healthy"
        }



class BrokenStore:

    def __init__(self):
        self.name = "broken_store"


    async def health(self):
        raise Exception("connection failed")



# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_storage_manager_initialization():

    store1 = FakeStore("document")
    store2 = FakeStore("vector")


    manager = StorageManager(
        document_store=store1,
        vector_store=store2,
    )


    await manager.initialize()


    assert store1.initialized is True
    assert store2.initialized is True



@pytest.mark.asyncio
async def test_storage_manager_close():

    store = FakeStore()


    manager = StorageManager(
        document_store=store
    )


    await manager.close()


    assert store.closed is True



def test_storage_transaction_creation():

    manager = StorageManager()


    transaction = manager.transaction()


    assert isinstance(
        transaction,
        StorageTransaction
    )



@pytest.mark.asyncio
async def test_storage_health():

    document_store = FakeStore(
        "documents"
    )

    vector_store = FakeStore(
        "vectors"
    )


    manager = StorageManager(
        document_store=document_store,
        vector_store=vector_store,
    )


    result = await manager.health()


    assert result == {
        "documents": {
            "status": "healthy"
        },
        "vectors": {
            "status": "healthy"
        },
    }



@pytest.mark.asyncio
async def test_storage_health_handles_failure():

    broken = BrokenStore()


    manager = StorageManager(
        document_store=broken
    )


    result = await manager.health()


    assert result["broken_store"]["status"] == "error"

    assert (
        result["broken_store"]["message"]
        ==
        "connection failed"
    )



@pytest.mark.asyncio
async def test_storage_manager_allows_missing_stores():

    manager = StorageManager()


    await manager.initialize()

    await manager.close()


    health = await manager.health()


    assert health == {}



def test_storage_manager_stores_iterator():

    document = FakeStore(
        "documents"
    )

    manager = StorageManager(
        document_store=document
    )


    stores = manager._stores()


    assert document in stores