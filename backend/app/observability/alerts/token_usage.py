"""
Token Usage Alert Engine

Monitors:
- Prompt tokens
- Completion tokens
- Total tokens
- Context window usage
- Token spikes
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional



@dataclass
class TokenAlert:
    service: str
    total_tokens: int
    threshold: int
    severity: str
    timestamp: datetime
    message: str



class TokenUsageMonitor:
    """
    Detects abnormal token consumption.
    """

    def __init__(
        self,
        default_threshold: int = 100000
    ):

        self.default_threshold = default_threshold


    def check(
        self,
        service: str,
        prompt_tokens: int,
        completion_tokens: int,
        threshold: Optional[int] = None
    ) -> Optional[TokenAlert]:


        limit = (
            threshold
            if threshold
            else self.default_threshold
        )


        total_tokens = (
            prompt_tokens +
            completion_tokens
        )


        if total_tokens <= limit:
            return None


        severity = self._severity(
            total_tokens,
            limit
        )


        return TokenAlert(

            service=service,

            total_tokens=total_tokens,

            threshold=limit,

            severity=severity,

            timestamp=datetime.utcnow(),

            message=(
                f"{service} consumed "
                f"{total_tokens} tokens"
            )
        )



    def _severity(
        self,
        tokens: int,
        limit: int
    ) -> str:


        ratio = tokens / limit


        if ratio >= 3:
            return "critical"

        if ratio >= 2:
            return "warning"

        return "info"