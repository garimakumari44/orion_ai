"""
Identifier utilities.

Generates deterministic and random IDs used throughout the
knowledge system.
"""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

from .hashing import hash_text


# ------------------------------------------------------------------
# UUIDs
# ------------------------------------------------------------------


def uuid4_str() -> str:
    """
    Random UUID.
    """

    return str(uuid.uuid4())


def uuid5_str(
    namespace: uuid.UUID,
    name: str,
) -> str:
    """
    Deterministic UUID.
    """

    return str(uuid.uuid5(namespace, name))


# ------------------------------------------------------------------
# Document IDs
# ------------------------------------------------------------------


def document_id(
    source: str,
    content: str,
) -> str:
    """
    Deterministic document ID.

    Same source + same content
    => same ID
    """

    return hash_text(
        f"{source}:{content}"
    )


def chunk_id(
    document_id: str,
    index: int,
) -> str:
    """
    Stable chunk identifier.
    """

    return hash_text(
        f"{document_id}:{index}"
    )


def entity_id(
    name: str,
    entity_type: str,
) -> str:
    """
    Deterministic entity ID.
    """

    return hash_text(
        f"{entity_type}:{name.lower()}"
    )


def relation_id(
    source_entity: str,
    target_entity: str,
    relation: str,
) -> str:
    """
    Graph edge identifier.
    """

    return hash_text(
        f"{source_entity}:{relation}:{target_entity}"
    )


# ------------------------------------------------------------------
# Random IDs
# ------------------------------------------------------------------


def random_id(
    length: int = 16,
) -> str:
    """
    URL-safe random string.
    """

    return secrets.token_hex(length // 2)


def session_id() -> str:
    """
    Session identifier.
    """

    return uuid4_str()


# ------------------------------------------------------------------
# Time IDs
# ------------------------------------------------------------------


def timestamp_id() -> str:
    """
    Example:
        20260719T104522Z
    """

    return datetime.now(
        UTC
    ).strftime("%Y%m%dT%H%M%SZ")


def run_id() -> str:
    """
    Pipeline execution ID.

    Example:
        run_20260719T104522Z_1af2e8bc
    """

    return (
        "run_"
        + timestamp_id()
        + "_"
        + random_id(8)
    )