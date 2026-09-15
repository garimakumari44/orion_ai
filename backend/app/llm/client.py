"""
OpenAI-compatible LLM client.

This class is a thin wrapper around the OpenAI SDK.

Architecture

Application
    │
    ▼
LLMManager
    │
    ▼
ProviderRouter
    │
    ▼
Provider
    │
    ▼
LLMClient
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI


class LLMClient:
    """
    Thin wrapper around the OpenAI-compatible SDK.

    Responsibilities
    ----------------
    - Execute chat completion requests
    - Return plain text responses
    - Hide OpenAI SDK details

    This class performs no routing,
    provider selection,
    or model selection.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
    ) -> None:
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def generate(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """
        Execute a chat completion request.

        Parameters
        ----------
        model:
            Model identifier.

        messages:
            OpenAI-format messages.

        temperature:
            Sampling temperature.

        max_tokens:
            Maximum output tokens.

        kwargs:
            Extra provider-specific parameters.

        Returns
        -------
        str
            Generated response.
        """

        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        if (
            not response.choices
            or response.choices[0].message is None
            or response.choices[0].message.content is None
        ):
            return ""

        return response.choices[0].message.content

    def health_check(self, *, model: str) -> bool:
        """
        Verify provider connectivity.
        """

        try:
            self.generate(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": "Reply with exactly one word: OK",
                    }
                ],
                temperature=0,
                max_tokens=5,
            )
            return True

        except Exception:
            return False