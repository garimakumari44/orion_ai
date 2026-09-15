"""
Global constants used by observability layer.

Includes:
- Event names
- Metric names
- Log levels
- Trace categories
"""


class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventType:
    """
    AI system lifecycle events.
    """

    REQUEST_STARTED = "request.started"
    REQUEST_COMPLETED = "request.completed"
    REQUEST_FAILED = "request.failed"

    LLM_REQUEST = "llm.request"
    LLM_RESPONSE = "llm.response"
    LLM_ERROR = "llm.error"

    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"

    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"

    RETRIEVAL_STARTED = "retrieval.started"
    RETRIEVAL_COMPLETED = "retrieval.completed"

    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"


class MetricName:
    """
    Metrics collected by system.
    """

    REQUEST_LATENCY = "request_latency_ms"

    LLM_LATENCY = "llm_latency_ms"

    TOKEN_INPUT = "tokens.input"
    TOKEN_OUTPUT = "tokens.output"

    LLM_COST = "llm.cost"

    CACHE_HIT_RATE = "cache.hit_rate"

    RETRIEVAL_SCORE = "retrieval.score"

    AGENT_EXECUTION_TIME = "agent.execution_time"

    ERROR_COUNT = "errors.total"


class TraceCategory:

    API = "api"

    LLM = "llm"

    AGENT = "agent"

    TOOL = "tool"

    RETRIEVAL = "retrieval"

    MEMORY = "memory"