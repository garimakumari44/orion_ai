# storage/stores/vector_store.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class VectorStore(ABC):

    @abstractmethod
    async def add(
        self,
        vector_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ):
        pass


    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ):
        pass


    @abstractmethod
    async def delete(
        self,
        vector_id: str,
    ):
        pass



class InMemoryVectorStore(VectorStore):


    def __init__(self):

        self.vectors = {}



    async def initialize(self):
        """
        Initialize in-memory vector storage.
        """

        self.vectors = {}



    async def close(self):
        """
        Cleanup vector storage.
        """

        self.vectors.clear()



    async def add(
        self,
        vector_id,
        embedding,
        metadata,
    ):

        self.vectors[vector_id] = {

            "embedding": embedding,

            "metadata": metadata,
        }



    async def search(
        self,
        query_vector,
        top_k=5,
        filters=None,
    ):

        """
        Temporary similarity search.

        Production:
        replace with Qdrant/FAISS
        """

        results = []


        for vector_id, item in self.vectors.items():

            results.append({

                "id": vector_id,

                "score": 0.0,

                "metadata": item["metadata"],

            })


        return results[:top_k]



    async def delete(
        self,
        vector_id,
    ):

        self.vectors.pop(
            vector_id,
            None,
        )