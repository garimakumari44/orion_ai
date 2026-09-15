"""
app/llm/providers/openrouter.py

Canonical OpenRouter LLM Provider.

Application code must not communicate with OpenRouter directly.

Architecture:

    LLMManager
         |
         v
    ModelRouter
         |
         v
    ProviderRouter
         |
         v
    OpenRouterProvider
         |
         v
    OpenRouter API
"""

from __future__ import annotations

from typing import Any, Iterator

from openai import OpenAI

from .base import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):

    PROVIDER_NAME = "openrouter"

    DEFAULT_BASE_URL = (
        "https://openrouter.ai/api/v1"
    )

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        app_name: str | None = None,
        app_url: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        task_models: dict[str, str] | None = None,
        embedding_model: str = (
            "openai/text-embedding-3-small"
        ),
        **config: Any,
    ) -> None:

        if not isinstance(
            api_key,
            str,
        ):
            raise TypeError(
                "api_key must be a string."
            )

        if not api_key.strip():
            raise ValueError(
                "OpenRouter api_key cannot be empty."
            )

        if not isinstance(
            model,
            str,
        ):
            raise TypeError(
                "model must be a string."
            )

        if not model.strip():
            raise ValueError(
                "OpenRouter model cannot be empty."
            )

        if app_name is not None and not isinstance(
            app_name,
            str,
        ):
            raise TypeError(
                "app_name must be a string or None."
            )

        if app_url is not None and not isinstance(
            app_url,
            str,
        ):
            raise TypeError(
                "app_url must be a string or None."
            )

        if timeout is not None:

            if isinstance(
                timeout,
                bool,
            ) or not isinstance(
                timeout,
                (int, float),
            ):
                raise TypeError(
                    "timeout must be numeric or None."
                )

            if timeout <= 0:
                raise ValueError(
                    "timeout must be greater than zero."
                )

        if task_models is not None:

            if not isinstance(
                task_models,
                dict,
            ):
                raise TypeError(
                    "task_models must be a dictionary."
                )

        if not isinstance(
            embedding_model,
            str,
        ):
            raise TypeError(
                "embedding_model must be a string."
            )

        if not embedding_model.strip():
            raise ValueError(
                "embedding_model cannot be empty."
            )

        resolved_base_url = (
            base_url
            or self.DEFAULT_BASE_URL
        )

        if not isinstance(
            resolved_base_url,
            str,
        ):
            raise TypeError(
                "base_url must be a string."
            )

        resolved_base_url = (
            resolved_base_url.strip()
        )

        if not resolved_base_url:
            resolved_base_url = (
                self.DEFAULT_BASE_URL
            )

        normalized_task_models: dict[str, str] = {}

        if task_models:

            for task_name, model_name in task_models.items():

                if not isinstance(
                    task_name,
                    str,
                ):
                    continue

                if not isinstance(
                    model_name,
                    str,
                ):
                    continue

                task_name = task_name.strip().lower()
                model_name = model_name.strip()

                if not task_name or not model_name:
                    continue

                normalized_task_models[
                    task_name
                ] = model_name

        super().__init__(
            api_key=api_key,
            model=model,
            app_name=app_name,
            app_url=app_url,
            base_url=resolved_base_url,
            timeout=timeout,
            task_models=normalized_task_models,
            embedding_model=embedding_model.strip(),
            **config,
        )

        self._base_url = resolved_base_url
        self._timeout = timeout

        self.client = OpenAI(
            api_key=api_key,
            base_url=resolved_base_url,
            timeout=timeout,
        )

        self.headers: dict[str, str] = {}

        if app_name and app_name.strip():
            self.headers[
                "X-Title"
            ] = app_name.strip()

        if app_url and app_url.strip():
            self.headers[
                "HTTP-Referer"
            ] = app_url.strip()

    # ======================================================================
    # IDENTITY
    # ======================================================================

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

    # ======================================================================
    # MODEL INFORMATION
    # ======================================================================

    def default_model(self) -> str:
        return super().default_model()

    def configured_models(self) -> dict[str, str]:
        return super().configured_models()

    def supports_model(
        self,
        model: str,
    ) -> bool:

        if not isinstance(
            model,
            str,
        ):
            return False

        model = model.strip()

        if not model:
            return False

        # OpenRouter supports arbitrary model identifiers.
        #
        # We therefore do not restrict the provider to only the
        # configured local model list.
        return True

    # ======================================================================
    # GENERATE
    # ======================================================================

    def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:

        self.validate_prompt(
            prompt
        )

        if system_prompt is not None:

            if not isinstance(
                system_prompt,
                str,
            ):
                raise TypeError(
                    "system_prompt must be a string or None."
                )

            if not system_prompt.strip():
                system_prompt = None

        messages: list[
            dict[str, Any]
        ] = []

        if system_prompt is not None:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ======================================================================
    # CHAT
    # ======================================================================

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:

        self.validate_messages(
            messages
        )

        self.validate_generation_parameters(
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response = (
            self.client.chat.completions.create(
                model=(
                    model
                    or self.default_model()
                ),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers=(
                    self.headers or None
                ),
                **kwargs,
            )
        )

        if not response.choices:
            return ""

        message = response.choices[0].message

        if message is None:
            return ""

        content = message.content

        if content is None:
            return ""

        return str(content)

    # ======================================================================
    # STREAM
    # ======================================================================

    def stream(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Iterator[str]:

        self.validate_messages(
            messages
        )

        self.validate_generation_parameters(
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response = (
            self.client.chat.completions.create(
                model=(
                    model
                    or self.default_model()
                ),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_headers=(
                    self.headers or None
                ),
                **kwargs,
            )
        )

        for chunk in response:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta is None:
                continue

            content = delta.content

            if content:
                yield str(content)

    # ======================================================================
    # EMBEDDINGS
    # ======================================================================

    def embeddings(
        self,
        *,
        texts: list[str],
        model: str | None = None,
        **kwargs: Any,
    ) -> list[list[float]]:

        self.validate_texts(
            texts
        )

        embedding_model = (
            model
            or self.get_config(
                "embedding_model",
                "openai/text-embedding-3-small",
            )
        )

        if not isinstance(
            embedding_model,
            str,
        ):
            raise TypeError(
                "embedding_model must be a string."
            )

        embedding_model = (
            embedding_model.strip()
        )

        if not embedding_model:
            raise ValueError(
                "embedding_model cannot be empty."
            )

        response = (
            self.client.embeddings.create(
                model=embedding_model,
                input=texts,
                extra_headers=(
                    self.headers or None
                ),
                **kwargs,
            )
        )

        return [
            list(item.embedding)
            for item in response.data
        ]

    # ======================================================================
    # HEALTH
    # ======================================================================

    def health_check(self) -> bool:

        try:

            self.client.models.list(
                extra_headers=(
                    self.headers or None
                ),
            )

            return True

        except Exception:
            return False

    # ======================================================================
    # CAPABILITIES
    # ======================================================================

    def supports(
        self,
        capability: str,
    ) -> bool:

        if not isinstance(
            capability,
            str,
        ):
            return False

        capability = (
            capability.strip().lower()
        )

        return capability in {
            "chat",
            "generate",
            "streaming",
            "embeddings",
            "vision",
            "tools",
            "structured_output",
            "reasoning",
        }

    # ======================================================================
    # REPRESENTATION
    # ======================================================================

    def __repr__(self) -> str:

        return (
            "OpenRouterProvider("
            f"provider={self.provider_name!r}, "
            f"model={self.model!r}"
            ")"
        )