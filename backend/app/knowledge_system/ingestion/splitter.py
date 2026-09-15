from __future__ import annotations

import uuid
from typing import List

from .models import Chunk, ProcessingDocument


class TextSplitter:
    """
    Splits large documents into overlapping chunks.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 100,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(
        self,
        document: ProcessingDocument,
    ) -> List[Chunk]:

        text = document.text

        chunks = []

        start = 0
        index = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk_text = text[start:end]

            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    text=chunk_text,
                    index=index,
                    metadata=document.metadata.copy(),
                )
            )

            start += self.chunk_size - self.chunk_overlap
            index += 1

        return chunks