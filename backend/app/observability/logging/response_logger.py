"""
response_logger.py

Structured logging for successful LLM responses.
"""

from typing import Any, Dict, Optional
import time

from .logger import get_logger


logger = get_logger("response")


class ResponseLogger:
    """
    Handles logging of LLM responses.
    """

    def __init__(self):
        self.logger = logger


    def log_response(
        self,
        *,
        request_id: str,
        model: str,
        provider: str,
        response: Any,
        latency: Optional[float] = None,
        usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log successful model response.

        Args:
            request_id:
                Unique request identifier

            model:
                Model name

            provider:
                LLM provider

            response:
                Raw model response

            latency:
                Response generation time

            usage:
                Token usage information

            metadata:
                Extra context
        """

        event = {
            "event": "llm_response",

            "request_id": request_id,

            "model": model,

            "provider": provider,

            "latency_ms":
                round(latency * 1000, 2)
                if latency
                else None,

            "usage": usage or {},

            "response_length":
                self._response_length(response),

            "metadata": metadata or {},
        }


        self.logger.info(
            "LLM response completed",
            extra=event
        )


    def log_stream_chunk(
        self,
        *,
        request_id: str,
        chunk: str,
        index: int
    ):
        """
        Log streaming response chunks.
        """

        self.logger.debug(
            "LLM stream chunk",
            extra={
                "event": "stream_chunk",

                "request_id": request_id,

                "chunk_index": index,

                "chunk_size": len(chunk)
            }
        )


    def _response_length(
        self,
        response: Any
    ) -> int:
        """
        Calculate response size safely.
        """

        try:

            if isinstance(response, str):
                return len(response)


            if hasattr(response, "content"):
                return len(response.content)


            return len(str(response))


        except Exception:
            return 0