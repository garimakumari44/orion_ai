"""
Metadata validation utilities.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class MetadataValidator:
    """
    Validates metadata dictionaries.
    """

    REQUIRED_FIELDS = [
        "source",
        "created_at",
    ]

    @classmethod
    def validate(cls, metadata: Dict[str, Any]) -> List[str]:
        errors: List[str] = []

        if not isinstance(metadata, dict):
            return ["Metadata must be a dictionary."]

        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Missing required field '{field}'.")

        created = metadata.get("created_at")

        if created is not None:
            if isinstance(created, str):
                try:
                    datetime.fromisoformat(created)
                except ValueError:
                    errors.append("created_at must be ISO datetime.")

            elif not isinstance(created, datetime):
                errors.append("created_at has invalid type.")

        source = metadata.get("source")

        if source is not None and not isinstance(source, str):
            errors.append("source must be string.")

        return errors

    @classmethod
    def is_valid(cls, metadata: Dict[str, Any]) -> bool:
        return len(cls.validate(metadata)) == 0