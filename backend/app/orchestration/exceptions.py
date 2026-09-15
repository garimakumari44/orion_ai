"""
Centralized exception hierarchy for Orion AI System.

All custom exceptions should inherit from OrionError.
This allows the system to:

- classify failures
- retry recoverable errors
- trigger fallbacks
- log meaningful error types
- expose safe messages to APIs
"""

from __future__ import annotations

from typing import Optional


class OrionError(Exception):
    """
    Base exception for the entire Orion system.
    """

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        recoverable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


# ==========================================================
# Planning Errors
# ==========================================================

class PlanningError(OrionError):
    """Raised when planning fails."""


class InvalidPlanError(PlanningError):
    """Generated plan is invalid."""


class TaskDependencyError(PlanningError):
    """Task dependency graph is invalid."""


# ==========================================================
# Execution Errors
# ==========================================================

class ExecutionError(OrionError):
    """Raised during task execution."""


class TaskExecutionError(ExecutionError):
    """Individual task execution failed."""


class WorkerUnavailableError(ExecutionError):
    """No worker available."""


class TaskTimeoutError(ExecutionError):
    """Task exceeded timeout."""


class RetryLimitExceededError(ExecutionError):
    """Maximum retries exceeded."""


# ==========================================================
# Tool Errors
# ==========================================================

class ToolError(OrionError):
    """Base tool exception."""


class ToolNotFoundError(ToolError):
    """Requested tool not registered."""


class ToolExecutionError(ToolError):
    """Tool execution failed."""


class ToolValidationError(ToolError):
    """Invalid tool inputs."""


class ToolTimeoutError(ToolError):
    """Tool timeout."""


class ToolUnavailableError(ToolError):
    """Tool currently unavailable."""


# ==========================================================
# Registry Errors
# ==========================================================

class RegistryError(OrionError):
    """Tool registry errors."""


class DuplicateToolError(RegistryError):
    """Tool already exists."""


class CapabilityNotFoundError(RegistryError):
    """Capability not found."""


# ==========================================================
# Routing Errors
# ==========================================================

class RoutingError(OrionError):
    """Tool selection/routing failed."""


class NoSuitableToolError(RoutingError):
    """No tool can satisfy requested capability."""


# ==========================================================
# Model Errors
# ==========================================================

class ModelError(OrionError):
    """LLM/model related errors."""


class ModelUnavailableError(ModelError):
    """LLM unavailable."""


class ModelRateLimitError(ModelError):
    """Rate limited by model provider."""


class InvalidModelResponseError(ModelError):
    """Model returned invalid output."""


# ==========================================================
# Validation Errors
# ==========================================================

class ValidationError(OrionError):
    """Generic validation error."""


class ConfigurationError(OrionError):
    """Configuration missing or invalid."""


class AuthenticationError(OrionError):
    """Authentication failed."""


class AuthorizationError(OrionError):
    """Permission denied."""