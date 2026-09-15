# models/health.py

from datetime import datetime
from typing import Dict, Any, Optional, List

from enum import Enum

from pydantic import BaseModel, Field



class HealthStatus(str, Enum):
    """
    Overall health state of a service.
    """

    HEALTHY = "healthy"

    DEGRADED = "degraded"

    UNHEALTHY = "unhealthy"

    UNKNOWN = "unknown"



class CheckStatus(str, Enum):
    """
    Individual health check result.
    """

    PASS = "pass"

    FAIL = "fail"

    WARNING = "warning"



class ComponentType(str, Enum):
    """
    System component categories.
    """

    API = "api"

    DATABASE = "database"

    CACHE = "cache"

    QUEUE = "queue"

    LLM = "llm"

    VECTOR_DB = "vector_db"

    STORAGE = "storage"

    GPU = "gpu"

    EXTERNAL_API = "external_api"



class HealthCheck(BaseModel):
    """
    Individual health check.

    Example:

    Check:
        OpenAI API reachable
        PostgreSQL connected
        Redis available
    """


    name: str


    status: CheckStatus


    message: Optional[str] = None


    latency_ms: Optional[float] = None


    checked_at: datetime = Field(
        default_factory=datetime.utcnow
    )


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )



class ComponentHealth(BaseModel):
    """
    Health information of a single component.

    Example:

    LLM Service
        |
        ├── Status: Healthy
        ├── Latency: 200ms
        └── Provider: OpenRouter
    """


    component_name: str


    component_type: ComponentType


    status: HealthStatus = HealthStatus.UNKNOWN


    version: Optional[str] = None


    uptime_seconds: Optional[float] = None


    checks: List[HealthCheck] = Field(
        default_factory=list
    )


    last_failure: Optional[datetime] = None


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )



    def add_check(
        self,
        check: HealthCheck
    ):
        """
        Add health check result.
        """

        self.checks.append(check)



    def mark_failure(self):
        """
        Mark component unhealthy.
        """

        self.status = HealthStatus.UNHEALTHY
        self.last_failure = datetime.utcnow()



    def mark_healthy(self):
        """
        Mark component healthy.
        """

        self.status = HealthStatus.HEALTHY



class SystemHealth(BaseModel):
    """
    Complete platform health snapshot.

    Represents:

    API
    |
    ├── LLM Service
    ├── Database
    ├── Vector DB
    ├── Cache
    └── Workers
    """


    service_name: str = "ai-platform"


    status: HealthStatus = HealthStatus.UNKNOWN


    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )


    components: List[ComponentHealth] = Field(
        default_factory=list
    )


    environment: Optional[str] = None


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )



    def add_component(
        self,
        component: ComponentHealth
    ):
        """
        Register system component.
        """

        self.components.append(component)



    def calculate_status(self):
        """
        Calculate overall platform health.
        """

        if any(
            c.status == HealthStatus.UNHEALTHY
            for c in self.components
        ):
            self.status = HealthStatus.UNHEALTHY


        elif any(
            c.status == HealthStatus.DEGRADED
            for c in self.components
        ):
            self.status = HealthStatus.DEGRADED


        else:
            self.status = HealthStatus.HEALTHY