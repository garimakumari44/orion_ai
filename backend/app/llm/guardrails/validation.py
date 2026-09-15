"""
Validation utilities for LLM pipelines.

Used to validate:

- prompts
- responses
- JSON outputs
- tool calls
- token limits
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]


class Validator:
    """
    General validation helper.
    """

    def validate_prompt(
        self,
        prompt: str,
        *,
        min_length: int = 1,
        max_length: int = 50000,
    ) -> ValidationResult:

        errors = []

        if not isinstance(prompt, str):
            errors.append("Prompt must be a string.")
            return ValidationResult(False, errors)

        if len(prompt.strip()) < min_length:
            errors.append("Prompt is empty.")

        if len(prompt) > max_length:
            errors.append("Prompt exceeds maximum length.")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    def validate_json(self, text: str) -> ValidationResult:
        try:
            json.loads(text)
            return ValidationResult(True, [])
        except Exception as exc:
            return ValidationResult(False, [str(exc)])

    def validate_required_fields(
        self,
        obj: Dict[str, Any],
        required: Iterable[str],
    ) -> ValidationResult:

        missing = [k for k in required if k not in obj]

        if missing:
            return ValidationResult(
                False,
                [f"Missing field: {k}" for k in missing],
            )

        return ValidationResult(True, [])

    def validate_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        schema: Dict[str, type],
    ) -> ValidationResult:

        errors = []

        for key, expected_type in schema.items():
            if key not in args:
                errors.append(f"Missing argument '{key}'")
                continue

            if not isinstance(args[key], expected_type):
                errors.append(
                    f"'{key}' must be {expected_type.__name__}"
                )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    def validate_response(
        self,
        response: Optional[str],
        *,
        max_length: int = 100000,
    ) -> ValidationResult:

        errors = []

        if response is None:
            errors.append("Response is None.")

        elif not isinstance(response, str):
            errors.append("Response must be a string.")

        elif len(response) > max_length:
            errors.append("Response exceeds maximum length.")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )