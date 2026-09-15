"""
Ollama Provider

Local LLM provider using the Ollama OpenAI-compatible API.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List

from openai import APIConnectionError, APITimeoutError, OpenAI

from .base import BaseLLMProvider
from ..constants import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
)

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama implementation.

    Features
    --------
    - Local inference
    - Retry logic
    - OpenAI-compatible interface
    - Streaming support
    """

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434/v1",
        timeout: int = 120,
        retries: int = 3,
    ):
        self.model = model
        self.timeout = timeout
        self.retries = retries

        # Ollama ignores API key but OpenAI client requires one.
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",
            timeout=timeout,
        )

    # ---------------------------------------------------------
    # Text Generation
    # ---------------------------------------------------------

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        **kwargs,
    ) -> str:
        """
        Generate text from the local Ollama model.
        """

        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                return response.choices[0].message.content

            except (
                APIConnectionError,
                APITimeoutError,
            ) as exc:

                last_error = exc

                logger.warning(
                    "Ollama attempt %d/%d failed: %s",
                    attempt,
                    self.retries,
                    exc,
                )

                time.sleep(attempt)

            except Exception:
                logger.exception("Unexpected Ollama error")
                raise

        raise RuntimeError(
            f"Ollama failed after {self.retries} retries."
        ) from last_error

    # ---------------------------------------------------------
    # Streaming
    # ---------------------------------------------------------

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        **kwargs,
    ):
        """
        Stream generated tokens.
        """

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content

            if delta:
                yield delta