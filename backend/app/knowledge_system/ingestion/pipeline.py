from __future__ import annotations

from typing import List

from .deduplicator import Deduplicator
from .models import Chunk, ProcessingDocument
from .normalizer import TextNormalizer
from .splitter import TextSplitter


class ProcessingPipeline:
    """
    Runs all document processing steps.
    """

    def __init__(
        self,
        splitter: TextSplitter | None = None,
        normalizer: TextNormalizer | None = None,
        deduplicator: Deduplicator | None = None,
    ):
        self.splitter = splitter or TextSplitter()
        self.normalizer = normalizer or TextNormalizer()
        self.deduplicator = deduplicator or Deduplicator()

    def process(
        self,
        document: ProcessingDocument,
    ) -> List[Chunk]:

        document = self.normalizer.normalize(document)

        if self.deduplicator.is_duplicate(document):
            return []

        chunks = self.splitter.split(document)

        return chunks