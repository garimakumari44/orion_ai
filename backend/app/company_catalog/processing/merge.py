
"""
app/company_catalog/processing/merge.py

Company Merge

Merges normalized company data with an existing company record.

IMPORTANT ARCHITECTURAL RULES

- Operates only on dictionaries.
- Must not depend on SQLAlchemy Company.
- Must not create or use AsyncSession.
- Must not access repositories.
- Incoming meaningful values may enrich existing data.
- Meaningful existing values must never be replaced by
  None, empty strings, or empty containers.
- Existing fields absent from incoming data are preserved.

Input:
    existing: dict[str, Any] | None
    incoming: dict[str, Any]

Output:
    dict[str, Any]
"""

from __future__ import annotations

from typing import Any


class CompanyMerger:
    """
    Merge normalized provider data with an existing company
    dictionary.

    The merger is deliberately provider-agnostic and database-free.
    """

    @staticmethod
    def merge(
        existing: dict[str, Any] | None,
        incoming: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge incoming company data with an existing company.

        Rules:

        1. If no existing company exists, return a copy of incoming.
        2. Preserve meaningful existing values when incoming is empty.
        3. Preserve fields that exist only on the existing company.
        4. Prefer meaningful incoming values.
        5. Never allow None/empty incoming values to erase useful data.
        """

        if not isinstance(incoming, dict):
            raise TypeError(
                "CompanyMerger.merge() requires incoming "
                "to be a dictionary."
            )

        if existing is None:
            return dict(incoming)

        if not isinstance(existing, dict):
            raise TypeError(
                "CompanyMerger.merge() requires existing "
                "to be a dictionary or None."
            )

        # Start with existing data so fields that are absent
        # from the provider response are preserved.
        merged: dict[str, Any] = dict(existing)

        # Apply incoming values only when they are meaningful.
        for field, incoming_value in incoming.items():

            if CompanyMerger._has_value(incoming_value):
                merged[field] = incoming_value

            elif field not in merged:
                # Preserve the incoming schema when there is no
                # existing value for this field.
                merged[field] = incoming_value

        return merged

    # =========================================================
    # Value Validation
    # =========================================================

    @staticmethod
    def _has_value(value: Any) -> bool:
        """
        Return True when a value contains meaningful data.

        Meaningful:
            - non-empty strings
            - non-empty lists
            - non-empty tuples
            - non-empty sets
            - non-empty dictionaries
            - numbers
            - booleans
            - other non-None objects

        Not meaningful:
            - None
            - whitespace-only strings
            - empty containers
        """

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)

        return True

