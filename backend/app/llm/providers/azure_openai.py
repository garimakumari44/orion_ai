"""
Azure OpenAI Provider

Azure-hosted OpenAI implementation of the BaseLLMProvider.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Iterator, List

from openai import (
    APIConnectionError,
    APITimeoutError,
    AzureOpenAI,
    RateLimitError,
)

from .base import BaseLLMProvider
from ..constants import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
)

logger = logging.getLogger(__name__)


class AzureOpenAIProvider(BaseLLMProvider):
    """
    Azure OpenAI implementation.

    Features
    --------
    ✓ GPT-4o
    ✓ GPT-4.1
    ✓ GPT-5 (when available)
    ✓ Streaming
    ✓ Retry logic
    """

    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        deployment_name: str,
        api_version: str = "2025-01-01-preview",
        timeout: int = 60,
        retries: int = 3,
    ):
        self.deployment_name = deployment_name
        self.timeout = timeout
        self.retries = retries

        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
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

        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                return response.choices[0].message.content or ""

            except (
                APIConnectionError,
                APITimeoutError,
                RateLimitError,
            ) as exc:

                last_error = exc

                logger.warning(
                    "Azure OpenAI attempt %d/%d failed: %s",
                    attempt,
                    self.retries,
                    exc,
                )

                time.sleep(attempt)

            except Exception:
                logger.exception("Unexpected Azure OpenAI error")
                raise

        raise RuntimeError(
            "Azure OpenAI request failed after retries."
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
    ) -> Iterator[str]:

        stream = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta.content

            if delta:
                yield delta

    # ---------------------------------------------------------
    # Health Check
    # ---------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify that the Azure deployment is reachable.
        """
        try:
            self.generate(
                [{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            return True

        except Exception:
            return False