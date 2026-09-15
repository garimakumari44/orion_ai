"""
streaming/handlers.py

Simple event dispatcher used by the streaming pipeline.

Allows modules to subscribe to streaming events
without introducing direct dependencies.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from typing import Awaitable, Callable, Dict, List

from .events import StreamEvent, StreamEventType

logger = logging.getLogger(__name__)

EventHandler = Callable[[StreamEvent], Awaitable[None] | None]


class EventDispatcher:
    """
    Publish / Subscribe dispatcher.

    Example:

        dispatcher.subscribe(
            StreamEventType.LLM_TOKEN,
            token_handler
        )

        await dispatcher.publish(event)
    """

    def __init__(self):
        self._handlers: Dict[
            StreamEventType,
            List[EventHandler],
        ] = defaultdict(list)

    # --------------------------------------------------
    # Subscription
    # --------------------------------------------------

    def subscribe(
        self,
        event_type: StreamEventType,
        handler: EventHandler,
    ) -> None:
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(
        self,
        event_type: StreamEventType,
        handler: EventHandler,
    ) -> None:
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    # --------------------------------------------------
    # Publishing
    # --------------------------------------------------

    async def publish(self, event: StreamEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])

        if not handlers:
            return

        tasks = []

        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    handler(event)

            except Exception:
                logger.exception(
                    "Handler failed for %s",
                    event.event_type.value,
                )

        if tasks:
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            for result in results:
                if isinstance(result, Exception):
                    logger.exception(result)

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def clear(self) -> None:
        self._handlers.clear()

    def count(
        self,
        event_type: StreamEventType,
    ) -> int:
        return len(self._handlers.get(event_type, []))

    def registered_events(self):
        return {
            event.value: len(handlers)
            for event, handlers in self._handlers.items()
        }


# Singleton dispatcher used across the application.
dispatcher = EventDispatcher()