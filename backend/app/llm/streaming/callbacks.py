"""
Streaming callback implementations.

Callbacks can be attached to any streaming session.

Example:

    session = StreamingSession(
        callback=ConsoleCallback()
    )

or

    callback = CompositeCallback(
        ConsoleCallback(),
        MetricsCallback(),
    )
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Callable, List


class StreamCallback(ABC):
    """
    Base callback interface.
    """

    @abstractmethod
    def __call__(self, token: str):
        pass


# -------------------------------------------------------
# Console Output
# -------------------------------------------------------


class ConsoleCallback(StreamCallback):
    """
    Prints streamed text.
    """

    def __call__(self, token: str):

        print(token, end="", flush=True)


# -------------------------------------------------------
# Buffer
# -------------------------------------------------------


class BufferCallback(StreamCallback):
    """
    Saves streamed output.
    """

    def __init__(self):

        self.buffer: List[str] = []

    def __call__(self, token: str):

        self.buffer.append(token)

    @property
    def text(self):

        return "".join(self.buffer)

    def clear(self):

        self.buffer.clear()


# -------------------------------------------------------
# Metrics
# -------------------------------------------------------


class MetricsCallback(StreamCallback):
    """
    Tracks streaming metrics.
    """

    def __init__(self):

        self.start = time.time()

        self.tokens = 0

    def __call__(self, token: str):

        self.tokens += 1

    @property
    def duration(self):

        return time.time() - self.start

    @property
    def tokens_per_second(self):

        elapsed = max(self.duration, 1e-6)

        return self.tokens / elapsed


# -------------------------------------------------------
# Token Counter
# -------------------------------------------------------


class TokenCounterCallback(StreamCallback):

    def __init__(self):

        self.count = 0

    def __call__(self, token: str):

        self.count += 1


# -------------------------------------------------------
# Composite Callback
# -------------------------------------------------------


class CompositeCallback(StreamCallback):
    """
    Execute multiple callbacks.

    Example:

        CompositeCallback(
            ConsoleCallback(),
            MetricsCallback(),
            BufferCallback(),
        )
    """

    def __init__(self, *callbacks: StreamCallback):

        self.callbacks = callbacks

    def __call__(self, token: str):

        for callback in self.callbacks:

            callback(token)


# -------------------------------------------------------
# Custom Function Wrapper
# -------------------------------------------------------


class FunctionCallback(StreamCallback):
    """
    Wrap a normal function as callback.

    Example:

        def websocket_send(token):
            ...

        callback = FunctionCallback(websocket_send)
    """

    def __init__(self, fn: Callable[[str], None]):

        self.fn = fn

    def __call__(self, token: str):

        self.fn(token)