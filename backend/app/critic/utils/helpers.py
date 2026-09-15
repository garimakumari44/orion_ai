"""
helpers.py

Generic helper utilities.
"""

import time
import uuid
from typing import Any, Dict


def generate_id(
    prefix: str = ""
) -> str:
    """
    Generate unique identifier.

    Example:

    eval_a81f92
    """

    identifier = uuid.uuid4().hex[:8]

    if prefix:
        return f"{prefix}_{identifier}"

    return identifier



def current_timestamp() -> float:
    """
    Return unix timestamp.
    """

    return time.time()



def timestamp_ms() -> int:
    """
    Return timestamp in milliseconds.
    """

    return int(
        time.time() * 1000
    )



def get_nested(
    data: Dict,
    path: str,
    default: Any = None
) -> Any:
    """
    Safely access nested dictionary.

    Example:

    get_nested(
        result,
        "metrics.accuracy"
    )

    """

    keys = path.split(".")


    current = data

    for key in keys:

        if not isinstance(
            current,
            dict
        ):
            return default


        if key not in current:
            return default


        current = current[key]


    return current



def flatten_dict(
    data: Dict,
    parent_key: str = "",
    separator: str = "."
) -> Dict:
    """
    Flatten nested dictionaries.

    Example:

    {
      "score":{
          "accuracy":90
      }
    }

    becomes:

    {
      "score.accuracy":90
    }
    """

    result = {}


    for key, value in data.items():

        new_key = (
            f"{parent_key}{separator}{key}"
            if parent_key
            else key
        )


        if isinstance(
            value,
            dict
        ):

            result.update(
                flatten_dict(
                    value,
                    new_key,
                    separator
                )
            )

        else:
            result[new_key] = value


    return result



def clamp(
    value: float,
    minimum: float,
    maximum: float
) -> float:
    """
    Restrict value between range.

    Used for:
    - scores
    - confidence
    """

    return max(
        minimum,
        min(
            value,
            maximum
        )
    )



def percentage(
    value: float,
    total: float
) -> float:
    """
    Convert value to percentage.
    """

    if total == 0:
        return 0.0

    return (
        value / total
    ) * 100



def merge_dicts(
    first: Dict,
    second: Dict
) -> Dict:
    """
    Merge dictionaries.
    """

    result = first.copy()

    result.update(second)

    return result



class Timer:
    """
    Simple execution timer.

    Used for:
    - evaluator latency
    - pipeline profiling
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None


    def start(self):
        self.start_time = time.time()


    def stop(self):
        self.end_time = time.time()


    @property
    def elapsed(self):

        if (
            self.start_time is None
            or self.end_time is None
        ):
            return None


        return (
            self.end_time
            -
            self.start_time
        )