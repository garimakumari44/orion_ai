from __future__ import annotations

import hashlib

from .models import ProcessingDocument


class Deduplicator:
    """
    Removes duplicate documents using content hashing.
    """

    def __init__(self):
        self._hashes: set[str] = set()

    @staticmethod
    def _hash(text: str) -> str:

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def is_duplicate(
        self,
        document: ProcessingDocument,
    ) -> bool:

        h = self._hash(document.text)

        if h in self._hashes:
            return True

        self._hashes.add(h)

        return False