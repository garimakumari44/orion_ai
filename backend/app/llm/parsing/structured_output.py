"""
Structured output parser and validator.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.parsing.json_parser import JSONParser

logger = logging.getLogger(__name__)

T = TypeVar("T")


class StructuredOutputParser:
    """
    Converts LLM outputs into validated Python objects.

    Supports:
    - dict
    - Pydantic models
    - dataclasses
    """

    @staticmethod
    def parse_dict(text: str) -> Dict[str, Any]:
        """
        Parse response into dictionary.
        """

        data = JSONParser.loads(text)

        if not isinstance(data, dict):
            raise TypeError("Expected dictionary.")

        return data

    @staticmethod
    def parse_model(
        text: str,
        model: Type[BaseModel],
    ) -> BaseModel:
        """
        Parse into a Pydantic model.
        """

        data = JSONParser.loads(text)

        try:
            return model.model_validate(data)

        except ValidationError as e:
            logger.error(e)
            raise

    @staticmethod
    def parse_dataclass(
        text: str,
        cls: Type[T],
    ) -> T:
        """
        Parse into a dataclass.
        """

        data = JSONParser.loads(text)

        return cls(**data)

    @staticmethod
    def serialize(obj: Any) -> dict:
        """
        Convert supported object into dict.
        """

        if isinstance(obj, BaseModel):
            return obj.model_dump()

        if is_dataclass(obj):
            return asdict(obj)

        if isinstance(obj, dict):
            return obj

        raise TypeError(
            f"Unsupported type: {type(obj)}"
        )

    @staticmethod
    def validate(
        text: str,
        model: Optional[Type[BaseModel]] = None,
    ) -> bool:
        """
        Validate structured output.
        """

        try:
            if model is None:
                JSONParser.loads(text)
            else:
                StructuredOutputParser.parse_model(
                    text,
                    model,
                )

            return True

        except Exception:
            return False