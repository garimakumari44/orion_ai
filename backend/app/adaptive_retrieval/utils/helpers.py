"""
General helper utilities.

Used across:
- Knowledge System
- Adaptive Retrieval System
- RAG pipeline
- Storage layer
- Evaluation modules
"""

from typing import Any, Dict, List
import hashlib
import json
import re



# --------------------------------------------------
# Hashing utilities
# --------------------------------------------------

def generate_hash(
    value: str,
    algorithm: str = "sha256"
) -> str:
    """
    Generate deterministic hash.

    Used for:
    - document IDs
    - chunk IDs
    - cache keys
    - deduplication
    """

    if not isinstance(value, str):
        value = str(value)


    hash_func = getattr(
        hashlib,
        algorithm
    )


    return hash_func(
        value.encode("utf-8")
    ).hexdigest()



# --------------------------------------------------
# Text utilities
# --------------------------------------------------

def clean_text(
    text: str
) -> str:
    """
    Normalize text.

    Operations:
    - remove extra spaces
    - remove empty lines
    - normalize whitespace
    """

    if not text:
        return ""


    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text



def normalize_text(
    text: str
) -> str:
    """
    Lowercase normalized text.

    Useful for:
    - keyword matching
    - duplicate detection
    """

    return clean_text(text).lower()



# --------------------------------------------------
# Dictionary helpers
# --------------------------------------------------

def safe_get(
    data: Dict[str, Any],
    key: str,
    default=None
):
    """
    Safe dictionary access.

    Prevents KeyError.
    """

    if not isinstance(data, dict):
        return default


    return data.get(
        key,
        default
    )



def deep_get(
    data: Dict[str, Any],
    path: List[str],
    default=None
):
    """
    Nested dictionary access.

    Example:

    deep_get(
        user,
        ["profile","name"]
    )
    """

    current = data


    for key in path:

        if not isinstance(
            current,
            dict
        ):
            return default


        current = current.get(
            key
        )


        if current is None:
            return default


    return current



# --------------------------------------------------
# List utilities
# --------------------------------------------------

def flatten_list(
    items: List[List[Any]]
) -> List[Any]:
    """
    Flatten nested lists.

    Example:

    [[1,2],[3,4]]

    becomes:

    [1,2,3,4]
    """

    return [
        item
        for sublist in items
        for item in sublist
    ]



def chunk_list(
    items: List[Any],
    size: int
) -> List[List[Any]]:
    """
    Split list into batches.

    Used for:
    - batch embedding
    - batch retrieval
    - async processing
    """

    if size <= 0:
        raise ValueError(
            "Chunk size must be greater than zero"
        )


    return [
        items[i:i+size]
        for i in range(
            0,
            len(items),
            size
        )
    ]



# --------------------------------------------------
# Serialization helpers
# --------------------------------------------------

def json_encode(
    data: Any
) -> str:
    """
    Convert object to JSON string.
    """

    return json.dumps(
        data,
        default=str,
        ensure_ascii=False
    )



def json_decode(
    value: str
) -> Any:
    """
    Convert JSON string back.
    """

    return json.loads(value)



# --------------------------------------------------
# Object helpers
# --------------------------------------------------

def is_empty(
    value: Any
) -> bool:
    """
    Check empty values.
    """

    return (
        value is None
        or value == ""
        or value == []
        or value == {}
    )



def clamp(
    value: float,
    minimum: float,
    maximum: float
) -> float:
    """
    Restrict value between range.

    Used for:
    - score calibration
    - confidence values
    """

    return max(
        minimum,
        min(
            value,
            maximum
        )
    )