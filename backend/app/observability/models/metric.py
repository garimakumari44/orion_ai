# models/metric.py

from datetime import datetime
from typing import Dict, Optional, Any

from enum import Enum

from pydantic import BaseModel, Field



class MetricType(str, Enum):
    """
    Supported metric categories.
    """

    COUNTER = "counter"

    GAUGE = "gauge"

    HISTOGRAM = "histogram"



class MetricUnit(str, Enum):

    MILLISECONDS = "ms"

    SECONDS = "seconds"

    TOKENS = "tokens"

    BYTES = "bytes"

    PERCENT = "percent"

    USD = "usd"

    COUNT = "count"



class Metric(BaseModel):
    """
    Generic observability metric.
    """


    name: str = Field(
        ...,
        description="Metric name"
    )


    metric_type: MetricType



    value: float



    unit: MetricUnit



    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )


    service_name: str = "ai-platform"



    component: Optional[str] = None


    tags: Dict[str, str] = Field(
        default_factory=dict
    )


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )



    def add_tag(
        self,
        key:str,
        value:str
    ):

        self.tags[key] = value