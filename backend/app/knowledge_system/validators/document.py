"""
Document validation utilities.

Responsible for validating incoming documents before ingestion.
"""

from __future__ import annotations

from typing import List

from app.knowledge_system.models.document import Document


class DocumentValidator:
    """
    Validates document objects.
    """

    MAX_TITLE_LENGTH = 512
    MAX_CONTENT_LENGTH = 20_000_000  # 20 MB text

    @classmethod
    def validate(cls, document: Document) -> List[str]:
        """
        Returns list of validation errors.
        Empty list means valid.
        """

        errors: List[str] = []

        if not document.id:
            errors.append("Document id is missing.")

        if not document.title:
            errors.append("Document title is missing.")

        elif len(document.title) > cls.MAX_TITLE_LENGTH:
            errors.append("Document title too long.")

        if not document.content:
            errors.append("Document content is empty.")

        elif len(document.content) > cls.MAX_CONTENT_LENGTH:
            errors.append("Document exceeds maximum size.")

        if document.metadata is None:
            errors.append("Metadata missing.")

        return errors

    @classmethod
    def is_valid(cls, document: Document) -> bool:
        return len(cls.validate(document)) == 0