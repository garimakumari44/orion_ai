from typing import List, Dict, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class VectorDocument:
    id: str
    embedding: List[float]
    metadata: Dict[str, Any]


class VectorIndex:
    """
    Semantic vector index.

    Responsible for:
    - storing embeddings
    - similarity search
    - deleting vectors
    """

    def __init__(self):
        self.documents: Dict[str, VectorDocument] = {}


    def add(
        self,
        document_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """
        Add document vector.
        """

        document = VectorDocument(
            id=document_id,
            embedding=embedding,
            metadata=metadata
        )

        self.documents[document_id] = document



    def delete(self, document_id: str):
        """
        Remove vector.
        """

        if document_id in self.documents:
            del self.documents[document_id]



    def similarity(
        self,
        query_vector,
        document_vector
    ):

        """
        Cosine similarity
        """

        q = np.array(query_vector)
        d = np.array(document_vector)

        score = np.dot(q,d) / (
            np.linalg.norm(q)
            *
            np.linalg.norm(d)
        )

        return float(score)



    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ):

        results = []


        for doc in self.documents.values():

            score = self.similarity(
                query_embedding,
                doc.embedding
            )

            results.append(
                {
                    "id": doc.id,
                    "score": score,
                    "metadata": doc.metadata
                }
            )


        results.sort(
            key=lambda x:x["score"],
            reverse=True
        )


        return results[:top_k]



    def count(self):

        return len(self.documents)