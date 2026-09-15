"""
Utility package exports.
"""

from .text import *
from .similarity import *

from .json_utils import (
    safe_json_loads,
    json_dumps,
    save_json,
    load_json,
    validate_json_structure,
    extract_json_block
)

from .helpers import (
    generate_id,
    current_timestamp,
    timestamp_ms,
    get_nested,
    flatten_dict,
    clamp,
    percentage,
    merge_dicts,
    Timer
)


__all__ = [
    "safe_json_loads",
    "json_dumps",
    "save_json",
    "load_json",
    "validate_json_structure",
    "extract_json_block",
    "generate_id",
    "current_timestamp",
    "timestamp_ms",
    "get_nested",
    "flatten_dict",
    "clamp",
    "percentage",
    "merge_dicts",
    "Timer"
]