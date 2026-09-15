from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class RunRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query to be planned")

    user_id: Optional[str] = Field(None, description="User identifier")

    session_id: Optional[str] = Field(None, description="Session tracking id")

    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional runtime context for planning"
    )


class ToolExecutionResult(BaseModel):
    """Standardized result returned by ToolExecutor."""

    tool_name: str
    success: bool
    data: Any
    latency: float
    error: Optional[str] = None