"""
streaming/events.py

Defines events emitted throughout the streaming pipeline.
These events allow different modules to communicate without
being tightly coupled.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict
import uuid


class StreamEventType(str, Enum):
    """Supported streaming event types."""

    STREAM_STARTED = "stream_started"
    STREAM_STOPPED = "stream_stopped"

    AUDIO_CHUNK = "audio_chunk"
    TRANSCRIPT_PARTIAL = "transcript_partial"
    TRANSCRIPT_FINAL = "transcript_final"

    LLM_STARTED = "llm_started"
    LLM_TOKEN = "llm_token"
    LLM_COMPLETED = "llm_completed"

    TTS_STARTED = "tts_started"
    TTS_AUDIO = "tts_audio"
    TTS_COMPLETED = "tts_completed"

    ERROR = "error"


@dataclass(slots=True)
class StreamEvent:
    """
    Generic event object exchanged across the streaming system.
    """

    event_type: StreamEventType
    payload: Dict[str, Any] = field(default_factory=dict)

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamEvent":
        return cls(
            event_type=StreamEventType(data["event_type"]),
            payload=data.get("payload", {}),
            source=data.get("source", "unknown"),
        )

    def __repr__(self) -> str:
        return (
            f"StreamEvent("
            f"type={self.event_type.value}, "
            f"source={self.source}, "
            f"id={self.event_id})"
        )