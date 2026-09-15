"""
validator.py

Validation utilities for tool execution.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List

from .schema import ToolCall


class ValidationError(Exception):
    """Raised when a tool call fails validation."""


class ToolValidator:
    """
    Validates tool calls before execution.
    """

    @staticmethod
    def validate_exists(
        tool_name: str,
        registry: Dict[str, Callable[..., Any]],
    ) -> Callable[..., Any]:
        """
        Ensure a tool exists.
        """

        if tool_name not in registry:
            raise ValidationError(f"Unknown tool '{tool_name}'.")

        return registry[tool_name]

    @staticmethod
    def validate_required_args(
        function: Callable[..., Any],
        arguments: Dict[str, Any],
    ) -> None:
        """
        Ensure all required arguments are present.
        """

        signature = inspect.signature(function)

        for name, parameter in signature.parameters.items():

            required = (
                parameter.default is inspect.Parameter.empty
                and parameter.kind
                not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                )
            )

            if required and name not in arguments:
                raise ValidationError(
                    f"Missing required argument '{name}'."
                )

    @staticmethod
    def validate_unknown_args(
        function: Callable[..., Any],
        arguments: Dict[str, Any],
    ) -> None:
        """
        Prevent passing unexpected arguments.
        """

        signature = inspect.signature(function)

        allowed = set(signature.parameters.keys())

        unknown = set(arguments.keys()) - allowed

        if unknown:
            raise ValidationError(
                f"Unknown arguments: {sorted(unknown)}"
            )

    @staticmethod
    def validate_types(
        function: Callable[..., Any],
        arguments: Dict[str, Any],
    ) -> None:
        """
        Best-effort runtime type validation.
        """

        signature = inspect.signature(function)

        for name, value in arguments.items():

            parameter = signature.parameters.get(name)

            if parameter is None:
                continue

            annotation = parameter.annotation

            if annotation is inspect._empty:
                continue

            try:
                if not isinstance(value, annotation):
                    raise ValidationError(
                        f"'{name}' must be {annotation.__name__}"
                    )
            except TypeError:
                # Skip complex typing annotations (Union, List[int], etc.)
                pass

    @classmethod
    def validate(
        cls,
        call: ToolCall,
        registry: Dict[str, Callable[..., Any]],
    ) -> Callable[..., Any]:
        """
        Run every validation.
        """

        function = cls.validate_exists(call.tool_name, registry)

        cls.validate_required_args(
            function,
            call.arguments,
        )

        cls.validate_unknown_args(
            function,
            call.arguments,
        )

        cls.validate_types(
            function,
            call.arguments,
        )

        return function