"""
Serialization utilities.

Responsible for converting observability objects into
JSON-compatible dictionaries for:
- APIs
- Storage
- Exporters
- Dashboards
"""

from datetime import datetime
from dataclasses import asdict, is_dataclass
from typing import Any
import json


def serialize_datetime(value: datetime):
    """
    Convert datetime objects into ISO format.
    """

    if isinstance(value, datetime):
        return value.isoformat()

    return value



def serialize_object(obj: Any) -> dict:
    """
    Convert Python objects into serializable dictionaries.

    Supports:
    - dataclasses
    - dictionaries
    - objects with __dict__
    """

    if is_dataclass(obj):
        data = asdict(obj)

    elif isinstance(obj, dict):
        data = obj

    elif hasattr(obj, "__dict__"):
        data = vars(obj)

    else:
        return {
            "value": str(obj)
        }


    return convert_values(data)



def convert_values(data):
    """
    Recursively convert non JSON values.
    """

    if isinstance(data, dict):

        return {
            key: convert_values(value)
            for key, value in data.items()
        }


    if isinstance(data, list):

        return [
            convert_values(item)
            for item in data
        ]


    if isinstance(data, datetime):

        return data.isoformat()


    return data



def to_json(obj: Any, indent: int = 2) -> str:
    """
    Convert object into JSON string.
    """

    serialized = serialize_object(obj)

    return json.dumps(
        serialized,
        indent=indent,
        default=str
    )



def from_json(payload: str) -> dict:
    """
    Deserialize JSON string.
    """

    return json.loads(payload)



def safe_serialize(obj):
    """
    Safe serialization.

    Prevents monitoring failures caused by
    serialization errors.
    """

    try:
        return serialize_object(obj)

    except Exception as error:

        return {
            "serialization_error": str(error),
            "value": str(obj)
        }