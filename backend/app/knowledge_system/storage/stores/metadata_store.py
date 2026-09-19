"""
Storage interface for document metadata.

Supported implementations:
- PostgreSQL
- MongoDB
- SQLite
- Redis
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MetadataStore(ABC):
    """
    Metadata storage interface.
    """


    @abstractmethod
    async def save(
        self,
        object_id: str,
        metadata: Dict[str, Any],
    ) -> None:
        ...


    @abstractmethod
    async def get(
        self,
        object_id: str,
    ) -> Optional[Dict[str, Any]]:
        ...


    @abstractmethod
    async def update(
        self,
        object_id: str,
        metadata: Dict[str, Any],
    ) -> None:
        ...


    @abstractmethod
    async def delete(
        self,
        object_id: str,
    ) -> None:
        ...


    @abstractmethod
    async def search(
        self,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        ...



class InMemoryMetadataStore(MetadataStore):
    """
    Development implementation.
    """


    def __init__(self):

        self._store: Dict[
            str,
            Dict[str, Any]
        ] = {}



    async def initialize(self) -> None:
        """
        Initialize metadata storage.
        """

        self._store = {}



    async def close(self) -> None:
        """
        Cleanup metadata storage.
        """

        self._store.clear()



    async def save(
        self,
        object_id: str,
        metadata: Dict[str, Any],
    ) -> None:

        self._store[object_id] = metadata.copy()



    async def get(
        self,
        object_id: str,
    ) -> Optional[Dict[str, Any]]:

        return self._store.get(object_id)



    async def update(
        self,
        object_id: str,
        metadata: Dict[str, Any],
    ) -> None:

        existing = self._store.get(
            object_id,
            {},
        )

        existing.update(metadata)

        self._store[object_id] = existing



    async def delete(
        self,
        object_id: str,
    ) -> None:

        self._store.pop(
            object_id,
            None,
        )



    async def search(
        self,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        results = []


        for object_id, metadata in self._store.items():

            matched = True


            for key, value in filters.items():

                if metadata.get(key) != value:

                    matched = False
                    break


            if matched:

                results.append(
                    {
                        "id": object_id,
                        "metadata": metadata,
                    }
                )


        return results