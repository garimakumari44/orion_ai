"""
Common helper utilities for observability system.

Used by:
- logging
- tracing
- metrics
- alerts
- monitoring
"""

import uuid
import time
import os
import platform
from datetime import datetime, timezone
from typing import Any, Dict


def generate_id(prefix: str = "") -> str:
    """
    Generate unique identifiers.

    Example:
        trace_8f92ab3
    """

    uid = uuid.uuid4().hex[:12]

    if prefix:
        return f"{prefix}_{uid}"

    return uid



def current_timestamp() -> str:
    """
    Return UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



def unix_timestamp() -> float:
    """
    Return unix timestamp.
    """

    return time.time()



def get_system_info() -> Dict[str, Any]:
    """
    Collect basic system information.
    """

    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "processor": platform.processor()
    }



def get_environment() -> str:
    """
    Current runtime environment.
    """

    return os.getenv(
        "ENVIRONMENT",
        "development"
    )



def safe_execute(
    func,
    *args,
    **kwargs
):
    """
    Execute function safely.

    Prevent observability
    failures from crashing app.
    """

    try:
        return func(*args, **kwargs)

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }



def mask_sensitive_data(
    data: Dict[str, Any],
    keys=None
):
    """
    Remove sensitive values.

    Example:
        password -> ****
    """

    if keys is None:
        keys = [
            "password",
            "token",
            "api_key",
            "secret"
        ]


    cleaned = {}

    for key, value in data.items():

        if key.lower() in keys:
            cleaned[key] = "****"

        else:
            cleaned[key] = value


    return cleaned