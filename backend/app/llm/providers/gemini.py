"""
Gemini Provider

Google Gemini implementation of the BaseLLMProvider.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

from google import genai
from google.genai.errors import APIError

from .base import BaseLLMProvider
from ..constants import DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini implementation.

    Supports:
    - Retry logic
    - Temperature
    - Max tokens
    - System prompts
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        retries: int = 3,
    ):
        self.model = model
        self.timeout = timeout
        self.retries = retries

        self.client = genai.Client(api_key=api_key)

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        **kwargs,
    ) -> str:
        """
        Generate a completion from Gemini.
        """

        prompt = self._convert_messages(messages)

        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                )

                return response.text

            except APIError as exc:
                last_error = exc

                logger.warning(
                    "Gemini API attempt %d/%d failed: %s",
                    attempt,
                    self.retries,
                    exc,
                )

                time.sleep(attempt)

            except Exception as exc:
                logger.exception("Unexpected Gemini error")
                raise exc

        raise RuntimeError(
            f"Gemini failed after {self.retries} attempts"
        ) from last_error

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _convert_messages(messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style chat messages into a prompt for Gemini.
        """

        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System:\n{content}\n")

            elif role == "assistant":
                prompt_parts.append(f"Assistant:\n{content}\n")

            else:
                prompt_parts.append(f"User:\n{content}\n")

        return "\n".join(prompt_parts)