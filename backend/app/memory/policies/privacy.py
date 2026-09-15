from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, List


class PrivacyPolicy(ABC):
    """
    Base privacy policy.

    Responsible for sanitizing sensitive metadata
    before storage or retrieval.
    """

    @abstractmethod
    def sanitize(
        self,
        memory: Dict,
    ) -> Dict:
        raise NotImplementedError


class DefaultPrivacyPolicy(PrivacyPolicy):
    """
    Default privacy implementation.

    Removes sensitive fields and optionally
    masks confidential values.
    """

    DEFAULT_BLOCKED_FIELDS = {
        "password",
        "token",
        "api_key",
        "secret",
        "private_key",
        "access_token",
        "refresh_token",
        "credit_card",
        "cvv",
        "ssn",
    }

    def __init__(
        self,
        blocked_fields: List[str] | None = None,
        mask_email: bool = True,
    ):
        self.blocked_fields = set(
            blocked_fields or self.DEFAULT_BLOCKED_FIELDS
        )
        self.mask_email = mask_email

    def sanitize(
        self,
        memory: Dict,
    ) -> Dict:

        memory = deepcopy(memory)

        metadata = memory.get("metadata", {})

        for field in list(metadata.keys()):
            if field.lower() in self.blocked_fields:
                metadata.pop(field)

        if self.mask_email and "email" in metadata:
            metadata["email"] = self._mask_email(
                metadata["email"]
            )

        memory["metadata"] = metadata

        return memory

    @staticmethod
    def _mask_email(email: str) -> str:
        """
        Convert:

            alice@example.com

        into

            a****@example.com
        """

        if "@" not in email:
            return email

        username, domain = email.split("@", 1)

        if len(username) <= 1:
            username = "*"

        else:
            username = username[0] + "*" * (len(username) - 1)

        return f"{username}@{domain}"

    def sanitize_batch(
        self,
        memories: List[Dict],
    ) -> List[Dict]:
        """
        Sanitize a collection of memories.
        """

        return [
            self.sanitize(memory)
            for memory in memories
        ]