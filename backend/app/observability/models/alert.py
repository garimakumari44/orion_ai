# models/alert.py

from datetime import datetime
from typing import Dict, Any, Optional, List

from enum import Enum

from pydantic import BaseModel, Field



class AlertType(str, Enum):
    """
    Alert categories.
    """

    LATENCY = "latency"

    FAILURE = "failure"

    COST = "cost"

    TOKEN_USAGE = "token_usage"

    MEMORY = "memory"

    AVAILABILITY = "availability"

    SECURITY = "security"



class AlertSeverity(str, Enum):

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"

    CRITICAL = "critical"



class AlertStatus(str, Enum):

    OPEN = "open"

    ACKNOWLEDGED = "acknowledged"

    RESOLVED = "resolved"



class Alert(BaseModel):
    """
    Represents an operational alert.

    Example:

    IF:
        latency > 5 seconds

    THEN:
        Create Alert
    """


    alert_id: str



    alert_type: AlertType



    severity: AlertSeverity



    status: AlertStatus = AlertStatus.OPEN



    title: str



    description: str



    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


    resolved_at: Optional[datetime] = None



    service_name: str = "ai-platform"



    component: Optional[str] = None



    trace_id: Optional[str] = None



    metric_name: Optional[str] = None



    metric_value: Optional[float] = None



    threshold: Optional[float] = None



    labels: Dict[str, str] = Field(
        default_factory=dict
    )


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


    notifications_sent: List[str] = Field(
        default_factory=list
    )



    def resolve(self):
        """
        Mark alert as resolved.
        """

        self.status = AlertStatus.RESOLVED

        self.resolved_at = datetime.utcnow()



    def acknowledge(self):
        """
        Mark alert as acknowledged.
        """

        self.status = AlertStatus.ACKNOWLEDGED