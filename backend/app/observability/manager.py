"""
Central observability manager.

Responsible for:

- Structured logging
- Event tracking
- Metrics collection
- LLM monitoring
- Agent monitoring
- Cost tracking
"""


import time
import logging
import traceback

from typing import Dict, Any, Optional


from .config import ObservabilityConfig
from .constants import (
    EventType,
    LogLevel
)



class ObservabilityManager:


    def __init__(
        self,
        config: Optional[ObservabilityConfig] = None
    ):

        self.config = (
            config
            or ObservabilityConfig()
        )


        self.logger = logging.getLogger(
            self.config.service_name
        )


        self.logger.setLevel(
            self.config.log_level
        )


        self.metrics = {}


        self.events = []



    # -----------------------------
    # Logging
    # -----------------------------


    def log(
        self,
        message: str,
        level: str = LogLevel.INFO,
        metadata: Dict[str,Any] | None = None
    ):


        payload = {

            "message": message,

            "level": level,

            "metadata": metadata or {},

            "timestamp": time.time()

        }


        self.events.append(payload)


        if level == LogLevel.ERROR:

            self.logger.error(payload)


        elif level == LogLevel.WARNING:

            self.logger.warning(payload)


        else:

            self.logger.info(payload)



    # -----------------------------
    # Event Tracking
    # -----------------------------


    def track_event(
        self,
        event_name: str,
        data: Dict[str,Any] | None = None
    ):


        event = {

            "event": event_name,

            "data": data or {},

            "timestamp": time.time()

        }


        self.events.append(event)


        self.log(
            f"Event: {event_name}",
            metadata=data
        )



    # -----------------------------
    # Metrics
    # -----------------------------


    def increment_metric(
        self,
        name: str,
        value: int = 1
    ):


        if name not in self.metrics:

            self.metrics[name] = 0


        self.metrics[name] += value



    def record_metric(
        self,
        name: str,
        value: float
    ):

        self.metrics[name] = value



    def get_metrics(self):

        return self.metrics



    # -----------------------------
    # Timing
    # -----------------------------


    def start_timer(self):

        return time.perf_counter()



    def end_timer(
        self,
        name: str,
        start_time: float
    ):


        duration = (
            time.perf_counter()
            -
            start_time
        )


        self.record_metric(
            name,
            duration * 1000
        )


        return duration



    # -----------------------------
    # LLM Tracking
    # -----------------------------


    def track_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency: float,
        cost: float = 0
    ):


        self.track_event(

            EventType.LLM_RESPONSE,

            {

                "model": model,

                "input_tokens": input_tokens,

                "output_tokens": output_tokens,

                "latency": latency,

                "cost": cost

            }

        )


        self.increment_metric(
            "llm.calls"
        )



    # -----------------------------
    # Agent Tracking
    # -----------------------------


    def track_agent(
        self,
        agent_name: str,
        status: str,
        metadata=None
    ):


        self.track_event(

            f"agent.{status}",

            {

                "agent": agent_name,

                **(metadata or {})

            }

        )



    # -----------------------------
    # Error Tracking
    # -----------------------------


    def capture_exception(
        self,
        error: Exception
    ):


        self.log(

            str(error),

            level=LogLevel.ERROR,

            metadata={

                "traceback":
                traceback.format_exc()

            }

        )


        self.increment_metric(
            "errors.total"
        )



    # -----------------------------
    # Health
    # -----------------------------


    def health(self):

        return {

            "service":
            self.config.service_name,

            "environment":
            self.config.environment,

            "metrics":
            self.metrics,

            "events":
            len(self.events)

        }