"""
Request lifecycle logging.

Used for API and agent execution tracing.
"""


import time
import uuid
from typing import Optional


from .logger import get_logger



logger = get_logger(
    "request"
)



class RequestLogger:


    def __init__(
        self
    ):
        self.start_time = None



    def start_request(
        self,
        method: str,
        path: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log incoming request.
        """


        request_id = (
            request_id
            or str(uuid.uuid4())
        )


        self.start_time = time.time()


        logger.info(
            "request_started",
            extra={
                "event": "request_started",
                "request_id": request_id,
                "method": method,
                "path": path,
                "user_id": user_id,
                "timestamp": time.time()
            }
        )


        return request_id



    def end_request(
        self,
        request_id: str,
        status_code: int
    ):
        """
        Log completed request.
        """


        latency = None


        if self.start_time:

            latency = (
                time.time()
                -
                self.start_time
            )


        logger.info(
            "request_completed",
            extra={
                "event": "request_completed",
                "request_id": request_id,
                "status_code": status_code,
                "latency_ms": (
                    latency * 1000
                    if latency
                    else None
                ),
                "timestamp": time.time()
            }
        )