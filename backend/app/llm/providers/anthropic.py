"""
Anthropic provider implementation.
"""

from __future__ import annotations

from typing import Dict, Generator, List

from anthropic import Anthropic

from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider.

    Implements the common BaseLLMProvider interface.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        **kwargs,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            **kwargs,
        )

        self.client = Anthropic(api_key=api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str | None = None,
        max_tokens: int = 1024,
        **kwargs,
    ) -> str:
        """
        Generate a chat completion.
        """

        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs,
        )

        return "".join(
            block.text
            for block in response.content
            if getattr(block, "type", "") == "text"
        )

    def stream(
        self,
        messages: List[Dict[str, str]],
        system: str | None = None,
        max_tokens: int = 1024,
        **kwargs,
    ) -> Generator[str, None, None]:
        """
        Stream Claude responses.
        """

        with self.client.messages.stream(
            model=self.model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs,
        ) as stream:

            for text in stream.text_stream:
                yield text

    def embeddings(
        self,
        texts: List[str],
        **kwargs,
    ) -> List[List[float]]:
        """
        Anthropic currently does not provide a public
        embeddings API.
        """

        raise NotImplementedError(
            "Anthropic does not currently support embeddings."
        )

    def health_check(self) -> bool:
        """
        Verify the Anthropic API is reachable.
        """

        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[
                    {
                        "role": "user",
                        "content": "ping",
                    }
                ],
            )
            return True

        except Exception:
            return False