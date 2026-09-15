"""
Validation utilities for LLM outputs.
"""

from __future__ import annotations

import logging
from typing import Any, Type

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class OutputValidator:
    """
    Collection of validation helpers.
    """

    @staticmethod
    def validate_json(data: Any) -> bool:
        """
        Verify parsed JSON is valid.
        """

        return isinstance(data, (dict, list))

    @staticmethod
    def validate_schema(
        data: Any,
        schema: Type[BaseModel],
    ) -> BaseModel:
        """
        Validate against a Pydantic schema.
        """

        try:
            return schema.model_validate(data)

        except ValidationError as e:
            logger.error("Schema validation failed.")
            logger.error(e)

            raise

    @staticmethod
    def validate_required_fields(
        data: dict,
        required: list[str],
    ) -> None:
        """
        Ensure required keys exist.
        """

        missing = [
            field
            for field in required
            if field not in data
        ]

        if missing:
            raise ValueError(
                f"Missing required fields: {missing}"
            )

    @staticmethod
    def validate_type(
        value: Any,
        expected: Type,
    ) -> None:
        """
        Validate Python type.
        """

        if not isinstance(value, expected):
            raise TypeError(
                f"Expected {expected}, got {type(value)}"
            )

    @staticmethod
    def validate_non_empty(
        value: Any,
        field: str,
    ) -> None:
        """
        Ensure value is not empty.
        """

        if value in (
            None,
            "",
            [],
            {},
        ):
            raise ValueError(
                f"{field} cannot be empty."
            )

    @staticmethod
    def validate_range(
        value: float,
        *,
        minimum: float,
        maximum: float,
    ) -> None:
        """
        Validate numeric range.
        """

        if not minimum <= value <= maximum:
            raise ValueError(
                f"{value} not in range "
                f"{minimum}..{maximum}"
            )