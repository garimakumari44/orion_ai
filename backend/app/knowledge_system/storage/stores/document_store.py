# storage/stores/document_store.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class DocumentStore(ABC):
    """
    Abstract document storage interface.
    """

    @abstractmethod
    async def save(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        pass


    @abstractmethod
    async def get(
        self,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        pass


    @abstractmethod
    async def delete(
        self,
        document_id: str
    ):
        pass


    @abstractmethod
    async def list_documents(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        pass



class InMemoryDocumentStore(DocumentStore):

    def __init__(self):
        self.documents = {}
    
    async def initialize(self) -> None:
        """
        Initialize in-memory document storage.
        """

        self.documents = {}



    async def shutdown(self) -> None:
        """
        Cleanup storage.
        """

        self.documents.clear()


    async def save(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):

        self.documents[document_id] = {

            "id": document_id,

            "content": content,

            "metadata": metadata
        }



    async def get(
        self,
        document_id: str
    ):

        return self.documents.get(document_id)



    async def delete(
        self,
        document_id: str
    ):

        if document_id in self.documents:
            del self.documents[document_id]



    async def list_documents(
        self,
        limit=100
    ):

        return list(
            self.documents.values()
        )[:limit]