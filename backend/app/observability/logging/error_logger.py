"""
error_logger.py

Structured error logging for LLM systems.
"""

from typing import Any, Dict, Optional
import traceback


from .logger import get_logger


logger = get_logger("error")


class ErrorLogger:
    """
    Handles application and LLM error logging.
    """


    def __init__(self):

        self.logger = logger



    def log_error(
        self,
        *,
        request_id: Optional[str],
        error: Exception,
        component: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log application error.
        """


        error_event = {

            "event": "llm_error",

            "request_id": request_id,

            "component": component,

            "provider": provider,

            "model": model,

            "error_type":
                type(error).__name__,


            "error_message":
                str(error),


            "metadata":
                metadata or {},


            "stack_trace":
                traceback.format_exc()

        }


        self.logger.error(
            "LLM execution failed",
            extra=error_event
        )



    def log_provider_failure(
        self,
        *,
        provider: str,
        model: str,
        reason: str,
        request_id: Optional[str] = None
    ):
        """
        Log provider failure.

        Example:
        OpenRouter timeout
        OpenAI rate limit
        Gemini unavailable
        """

        self.logger.warning(
            "Provider failure",
            extra={

                "event":
                    "provider_failure",

                "request_id":
                    request_id,

                "provider":
                    provider,

                "model":
                    model,

                "reason":
                    reason
            }
        )



    def log_retry(
        self,
        *,
        request_id: str,
        attempt: int,
        max_attempts: int,
        error: Exception
    ):
        """
        Log retry attempts.
        """

        self.logger.warning(
            "Retrying failed request",
            extra={

                "event":
                    "retry",

                "request_id":
                    request_id,

                "attempt":
                    attempt,

                "max_attempts":
                    max_attempts,

                "error":
                    str(error)

            }
        )