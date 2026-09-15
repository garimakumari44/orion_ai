"""
Entity validation utilities.
"""

from __future__ import annotations

from typing import List

from app.knowledge_system.models.entity import Entity


class EntityValidator:
    """
    Validates extracted entities.
    """

    MAX_NAME_LENGTH = 512

    @classmethod
    def validate(cls, entity: Entity) -> List[str]:
        errors: List[str] = []

        if not entity.id:
            errors.append("Entity id missing.")

        if not entity.name:
            errors.append("Entity name missing.")

        elif len(entity.name) > cls.MAX_NAME_LENGTH:
            errors.append("Entity name too long.")

        if not entity.type:
            errors.append("Entity type missing.")

        if entity.confidence is not None:
            if not (0.0 <= entity.confidence <= 1.0):
                errors.append(
                    "Confidence must be between 0 and 1."
                )

        return errors

    @classmethod
    def is_valid(cls, entity: Entity) -> bool:
        return len(cls.validate(entity)) == 0