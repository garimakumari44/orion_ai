"""
json_utils.py

Utilities for JSON handling inside the critic framework.
"""

import json
from typing import Any, Dict, Optional


def safe_json_loads(
    data: str,
    default: Optional[Any] = None
) -> Any:
    """
    Safely parse JSON string.

    Useful for:
    - LLM structured outputs
    - evaluator responses
    - tool results
    """

    if not data:
        return default

    try:
        return json.loads(data)

    except json.JSONDecodeError:
        return default



def json_dumps(
    data: Any,
    indent: int = 2
) -> str:
    """
    Convert object into JSON string.

    Handles:
    - dictionaries
    - lists
    - evaluator results
    """

    return json.dumps(
        data,
        indent=indent,
        ensure_ascii=False,
        default=str
    )



def save_json(
    filepath: str,
    data: Any
) -> None:
    """
    Save JSON object to file.
    """

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
            default=str
        )



def load_json(
    filepath: str,
    default: Optional[Any] = None
) -> Any:
    """
    Load JSON file safely.
    """

    try:
        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):
        return default



def validate_json_structure(
    data: Dict,
    required_fields: list
) -> bool:
    """
    Check required keys exist.

    Example:

    validate_json_structure(
        result,
        [
            "score",
            "reason"
        ]
    )
    """

    if not isinstance(data, dict):
        return False

    return all(
        field in data
        for field in required_fields
    )



def extract_json_block(
    text: str
) -> Optional[dict]:
    """
    Extract JSON object from LLM response.

    Example:

    Text:
    "Here is result:
    {
      score: 90
    }"

    Returns:
    {
      score:90
    }
    """

    if not text:
        return None


    start = text.find("{")
    end = text.rfind("}")


    if start == -1 or end == -1:
        return None


    json_text = text[start:end + 1]


    return safe_json_loads(
        json_text
    )