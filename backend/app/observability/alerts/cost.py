"""
Cost Alert Engine

Tracks:
- LLM API spending
- Request cost
- Daily/monthly budget
- Cost spikes
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional



@dataclass
class CostAlert:

    service: str
    current_cost: float
    threshold: float
    currency: str
    severity: str
    timestamp: datetime
    message: str



class CostMonitor:
    """
    Monitors AI infrastructure costs.
    """

    def __init__(
        self,
        daily_budget: float = 50.0,
        currency: str = "USD"
    ):

        self.daily_budget = daily_budget
        self.currency = currency

        self.total_cost = 0.0



    def record_cost(
        self,
        service: str,
        cost: float,
        threshold: Optional[float] = None
    ) -> Optional[CostAlert]:


        self.total_cost += cost


        limit = (
            threshold
            if threshold
            else self.daily_budget
        )


        if self.total_cost <= limit:
            return None


        severity = self._severity(
            self.total_cost,
            limit
        )


        return CostAlert(

            service=service,

            current_cost=self.total_cost,

            threshold=limit,

            currency=self.currency,

            severity=severity,

            timestamp=datetime.utcnow(),

            message=(
                f"{service} exceeded "
                f"{self.currency}{limit} budget"
            )

        )



    def _severity(
        self,
        cost: float,
        limit: float
    ) -> str:


        ratio = cost / limit


        if ratio >= 3:
            return "critical"


        if ratio >= 1.5:
            return "warning"


        return "info"



    def reset_daily_usage(self):

        self.total_cost = 0.0