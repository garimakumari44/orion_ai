"""
Hashing utilities.

Provides deterministic hashing functions used across the
knowledge system.

Supported uses:
- Document deduplication
- Chunk fingerprints
- Metadata hashing
- Cache keys
- Version hashes
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SUPPORTED = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}


def hash_bytes(
    data: bytes,
    algorithm: str = "sha256",
) -> str:
    """
    Hash raw bytes.
    """

    if algorithm not in SUPPORTED:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    h = SUPPORTED[algorithm]()
    h.update(data)

    return h.hexdigest()


def hash_text(
    text: str,
    algorithm: str = "sha256",
    encoding: str = "utf-8",
) -> str:
    """
    Hash text.
    """

    return hash_bytes(
        text.encode(encoding),
        algorithm=algorithm,
    )


def hash_file(
    path: str | Path,
    algorithm: str = "sha256",
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Streaming file hash.
    """

    if algorithm not in SUPPORTED:
        raise ValueError(algorithm)

    h = SUPPORTED[algorithm]()

    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)

    return h.hexdigest()


def hash_json(
    obj: Any,
    algorithm: str = "sha256",
) -> str:
    """
    Deterministic JSON hash.

    Dictionaries are sorted automatically.
    """

    serialized = json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hash_text(serialized, algorithm)


def short_hash(
    text: str,
    length: int = 12,
) -> str:
    """
    Small readable hash.
    """

    return hash_text(text)[:length]