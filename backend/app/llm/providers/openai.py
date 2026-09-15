"""
OpenAI / OpenRouter provider implementation.
"""

from __future__ import annotations

from typing import Dict, Generator, List

from openai import OpenAI

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI-compatible provider.

    Works with:

    - OpenAI
    - OpenRouter
    - Together AI
    - Groq
    - Any OpenAI-compatible API
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            **kwargs,
        )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> str:
        """
        Generate a standard response.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,
        )

        return response.choices[0].message.content or ""

    def stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> Generator[str, None, None]:
        """
        Stream response chunks.
        """

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small",
        **kwargs,
    ) -> List[List[float]]:
        """
        Generate embeddings.
        """

        response = self.client.embeddings.create(
            model=model,
            input=texts,
            **kwargs,
        )

        return [item.embedding for item in response.data]

    def health_check(self) -> bool:
        """
        Verify provider availability.
        """

        try:
            self.client.models.list()
            return True
        except Exception:
            return False