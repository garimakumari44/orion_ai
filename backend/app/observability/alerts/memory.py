"""
Memory Alert Engine

Monitors:
- RAM usage
- Agent working memory
- Vector memory size
- Context memory pressure
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional



@dataclass
class MemoryAlert:

    component: str
    usage_percent: float
    threshold_percent: float
    severity: str
    timestamp: datetime
    message: str



class MemoryMonitor:
    """
    Detects memory pressure conditions.
    """

    def __init__(
        self,
        default_threshold: float = 85.0
    ):

        self.default_threshold = default_threshold



    def check(
        self,
        component: str,
        usage_percent: float,
        threshold: Optional[float] = None
    ) -> Optional[MemoryAlert]:


        limit = (
            threshold
            if threshold
            else self.default_threshold
        )


        if usage_percent <= limit:
            return None


        severity = self._severity(
            usage_percent,
            limit
        )


        return MemoryAlert(

            component=component,

            usage_percent=usage_percent,

            threshold_percent=limit,

            severity=severity,

            timestamp=datetime.utcnow(),

            message=(
                f"{component} memory usage "
                f"reached {usage_percent}%"
            )
        )



    def _severity(
        self,
        usage: float,
        limit: float
    ) -> str:


        ratio = usage / limit


        if ratio >= 1.2:
            return "critical"


        if ratio >= 1.05:
            return "warning"


        return "info"