"""
app/industry_catalog/processing/validator.py

Validation for canonical industry records.

Validation is deterministic and does not perform
external lookups.
"""

from __future__ import annotations

from typing import Any, Dict, List


class IndustryValidationError(ValueError):
    """
    Raised when industry metadata fails validation.
    """

    def __init__(
        self,
        errors: List[str],
    ) -> None:

        self.errors = errors

        message = "Industry validation failed: " + "; ".join(errors)

        super().__init__(message)


class IndustryValidator:
    """
    Validate normalized industry metadata.

    Important architectural rule:

        sector != industry

    Sector may be useful metadata, but it must never
    substitute for a missing industry classification.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(
        self,
        data: Dict[str, Any],
        *,
        raise_on_error: bool = True,
    ) -> bool:

        errors = self.get_errors(data)

        if errors and raise_on_error:
            raise IndustryValidationError(errors)

        return not errors

    # ------------------------------------------------------------------
    # Error collection
    # ------------------------------------------------------------------

    def get_errors(
        self,
        data: Dict[str, Any] | None,
    ) -> List[str]:

        errors: List[str] = []

        if not data:
            errors.append("Industry record is empty.")
            return errors

        industry = data.get("industry")

        if not industry:
            errors.append(
                "Industry classification is required."
            )

        # Sector must never be used as a fallback industry.
        if (
            data.get("sector")
            and data.get("industry")
            and data["sector"].strip().lower()
            == data["industry"].strip().lower()
        ):
            errors.append(
                "Sector and industry should not be identical "
                "unless the provider explicitly defines them that way."
            )

        self._validate_code(
            data.get("sic_code"),
            "SIC",
            errors,
        )

        self._validate_code(
            data.get("naics_code"),
            "NAICS",
            errors,
        )

        self._validate_string_length(
            data.get("industry"),
            "industry",
            errors,
        )

        self._validate_string_length(
            data.get("sub_industry"),
            "sub_industry",
            errors,
        )

        return errors

    # ------------------------------------------------------------------
    # Code validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_code(
        value: Any,
        name: str,
        errors: List[str],
    ) -> None:

        if value is None:
            return

        value = str(value).strip()

        if not value:
            return

        if not value.isalnum():
            errors.append(
                f"{name} code must be alphanumeric."
            )

    # ------------------------------------------------------------------
    # String validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_string_length(
        value: Any,
        field: str,
        errors: List[str],
        maximum: int = 500,
    ) -> None:

        if value is None:
            return

        if len(str(value)) > maximum:
            errors.append(
                f"{field} exceeds maximum length of {maximum}."
            )