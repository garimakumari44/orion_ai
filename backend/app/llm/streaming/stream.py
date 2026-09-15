"""
Streaming utilities.

Provides a unified interface for consuming streaming responses
from different LLM providers.

Supported chunk formats:
- OpenAI
- OpenRouter
- Anthropic
- Ollama
- Custom generators
"""

from __future__ import annotations

from typing import Any, Callable, Generator, Iterable, Iterator, Optional


class StreamProcessor:
    """
    Processes streaming responses and emits tokens.

    Example:
        processor = StreamProcessor()

        for token in processor.process(stream):
            print(token, end="")
    """

    def process(
        self,
        stream: Iterable[Any],
    ) -> Iterator[str]:
        """
        Extract text tokens from provider stream.
        """

        for chunk in stream:
            token = self.extract_token(chunk)

            if token:
                yield token

    @staticmethod
    def extract_token(chunk: Any) -> str:
        """
        Extract text from provider-specific chunk.
        """

        # ------------------------------------
        # OpenAI / OpenRouter
        # ------------------------------------
        try:
            if hasattr(chunk, "choices"):
                delta = chunk.choices[0].delta

                if hasattr(delta, "content"):
                    return delta.content or ""
        except Exception:
            pass

        # ------------------------------------
        # Anthropic
        # ------------------------------------
        try:
            if hasattr(chunk, "delta"):
                if hasattr(chunk.delta, "text"):
                    return chunk.delta.text or ""
        except Exception:
            pass

        # ------------------------------------
        # Ollama
        # ------------------------------------
        if isinstance(chunk, dict):

            if "message" in chunk:
                return chunk["message"].get("content", "")

            if "response" in chunk:
                return chunk["response"]

        if isinstance(chunk, str):
            return chunk

        return ""


class StreamAccumulator:
    """
    Collect streamed tokens into a final string.
    """

    def __init__(self):

        self._tokens: list[str] = []

    def add(self, token: str):

        self._tokens.append(token)

    def clear(self):

        self._tokens.clear()

    @property
    def text(self) -> str:

        return "".join(self._tokens)

    def __str__(self):

        return self.text


class StreamingSession:
    """
    High-level streaming helper.

    Combines:
        provider stream
        ↓
        token extraction
        ↓
        callback
        ↓
        accumulation
    """

    def __init__(
        self,
        callback: Optional[Callable[[str], None]] = None,
    ):

        self.callback = callback

        self.accumulator = StreamAccumulator()

        self.processor = StreamProcessor()

    def run(self, stream: Iterable[Any]) -> str:

        for token in self.processor.process(stream):

            self.accumulator.add(token)

            if self.callback:
                self.callback(token)

        return self.accumulator.text