"""
Serialization helpers.

Supports:
- dataclasses
- Pydantic models
- datetime
- UUID
- Enum
- pathlib.Path
- numpy arrays (optional)
- bytes

Useful for:
- JSON storage
- API responses
- Cache serialization
- Logging
"""

from __future__ import annotations

import base64
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID


def _default(obj: Any):
    """
    JSON serializer.
    """

    if is_dataclass(obj):
        return asdict(obj)

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode()

    try:
        import numpy as np

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, np.generic):
            return obj.item()

    except ImportError:
        pass

    raise TypeError(
        f"Object of type {type(obj).__name__} is not JSON serializable."
    )


def to_json(
    obj: Any,
    *,
    indent: int | None = 2,
    sort_keys: bool = False,
) -> str:
    """
    Serialize an object to JSON.
    """

    return json.dumps(
        obj,
        default=_default,
        ensure_ascii=False,
        indent=indent,
        sort_keys=sort_keys,
    )


def from_json(
    data: str,
) -> Any:
    """
    Deserialize JSON string.
    """

    return json.loads(data)


def to_bytes(
    obj: Any,
) -> bytes:
    """
    Serialize object to UTF-8 bytes.
    """

    return to_json(obj, indent=None).encode("utf-8")


def from_bytes(
    data: bytes,
) -> Any:
    """
    Deserialize UTF-8 bytes.
    """

    return from_json(data.decode("utf-8"))


def save_json(
    obj: Any,
    path: str | Path,
) -> None:
    """
    Save JSON to disk.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        to_json(obj),
        encoding="utf-8",
    )


def load_json(
    path: str | Path,
) -> Any:
    """
    Load JSON from disk.
    """

    return from_json(
        Path(path).read_text(encoding="utf-8")
    )