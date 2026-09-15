"""
app/llm/providers/base.py

Canonical LLM Provider Interface.

Every concrete LLM provider must implement this interface.

Architecture:

    Application
        |
        v
    LLMManager
        |
        v
    ModelRouter
        |
        v
    ProviderRouter
        |
        v
    BaseLLMProvider
        |
        +--> OpenRouter
        +--> OpenAI
        +--> Anthropic
        +--> Gemini
        +--> Ollama
        +--> future providers

This module contains NO vendor-specific logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterator


class BaseLLMProvider(ABC):
    """
    Canonical abstract interface implemented by every LLM provider.
    """

    def __init__(
        self,
        *,
        api_key: str = "",
        model: str,
        **config: Any,
    ) -> None:
        """
        Initialize the provider.

        Parameters
        ----------
        api_key:
            Authentication credential.

        model:
            Default model used by this provider.

        config:
            Provider-specific configuration.
        """

        if not isinstance(
            api_key,
            str,
        ):
            raise TypeError(
                "api_key must be a string."
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
                "model cannot be empty."
            )

        self.api_key = api_key
        self.model = model.strip()
        self.config = dict(config)

    # ======================================================================
    # PROVIDER IDENTITY
    # ======================================================================

    @property
    def provider_name(self) -> str:
        """
        Canonical provider identifier.
        """

        return self.__class__.__name__.lower()

    # ======================================================================
    # MODEL INFORMATION
    # ======================================================================

    def default_model(self) -> str:
        """
        Return the provider's default model.

        Concrete providers may override this when model resolution
        is more sophisticated.
        """

        model = self.model

        if not isinstance(
            model,
            str,
        ):
            raise RuntimeError(
                "Provider model must be a string."
            )

        model = model.strip()

        if not model:
            raise RuntimeError(
                "Provider model cannot be empty."
            )

        return model

    def configured_models(self) -> dict[str, str]:
        """
        Return task-specific model configuration.

        Expected format:

            {
                "chat": "...",
                "reasoning": "...",
                "fast": "...",
                "code": "...",
                "vision": "...",
                "cheap": "..."
            }

        Providers may override this method.

        By default, task-specific models can be supplied through
        provider configuration using:

            task_models={
                "reasoning": "...",
                "fast": "...",
                ...
            }
        """

        task_models = self.config.get(
            "task_models",
            {},
        )

        if task_models is None:
            return {}

        if not isinstance(
            task_models,
            dict,
        ):
            raise TypeError(
                "task_models must be a dictionary."
            )

        normalized: dict[str, str] = {}

        for task, model in task_models.items():

            if not isinstance(
                task,
                str,
            ):
                continue

            if not isinstance(
                model,
                str,
            ):
                continue

            task_name = task.strip().lower()
            model_name = model.strip()

            if not task_name:
                continue

            if not model_name:
                continue

            normalized[
                task_name
            ] = model_name

        return normalized

    def supports_model(
        self,
        model: str,
    ) -> bool:
        """
        Return whether this provider can use the specified model.

        The default implementation considers:

        1. The provider's default model.
        2. Any configured task-specific models.

        Concrete providers can override this with provider-specific
        model discovery or validation.
        """

        if not isinstance(
            model,
            str,
        ):
            return False

        model = model.strip()

        if not model:
            return False

        if model == self.default_model():
            return True

        return model in set(
            self.configured_models().values()
        )

    # ======================================================================
    # GENERATE
    # ======================================================================

    @abstractmethod
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
        """
        Generate a complete text response.
        """

        ...

    # ======================================================================
    # CHAT
    # ======================================================================

    @abstractmethod
    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """
        Generate a complete chat response.
        """

        ...

    # ======================================================================
    # STREAM
    # ======================================================================

    @abstractmethod
    def stream(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Iterator[str]:
        """
        Stream text fragments.

        Providers must yield plain strings.
        """

        ...

    # ======================================================================
    # EMBEDDINGS
    # ======================================================================

    @abstractmethod
    def embeddings(
        self,
        *,
        texts: list[str],
        model: str | None = None,
        **kwargs: Any,
    ) -> list[list[float]]:
        """
        Generate one embedding vector per input text.
        """

        ...

    # ======================================================================
    # HEALTH
    # ======================================================================

    @abstractmethod
    def health_check(self) -> bool:
        """
        Perform a lightweight provider availability check.

        Provider/network exceptions should not escape this method.
        """

        ...

    # ======================================================================
    # AVAILABILITY
    # ======================================================================

    def is_available(self) -> bool:
        """
        Compatibility wrapper around health_check().
        """

        try:
            return bool(
                self.health_check()
            )

        except Exception:
            return False

    # ======================================================================
    # CONFIGURATION
    # ======================================================================

    def get_config(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve provider-specific configuration.
        """

        if not isinstance(
            key,
            str,
        ):
            return default

        return self.config.get(
            key,
            default,
        )

    # ======================================================================
    # CAPABILITIES
    # ======================================================================

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Return whether the provider supports a capability.

        Concrete providers should override this method.
        """

        if not isinstance(
            capability,
            str,
        ):
            return False

        return False

    # ======================================================================
    # VALIDATION HELPERS
    # ======================================================================

    @staticmethod
    def validate_prompt(
        prompt: str,
    ) -> None:
        """
        Validate a text prompt.
        """

        if not isinstance(
            prompt,
            str,
        ):
            raise TypeError(
                "prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "prompt cannot be empty."
            )

    @staticmethod
    def validate_messages(
        messages: list[dict[str, Any]],
    ) -> None:
        """
        Validate canonical chat messages.
        """

        if not isinstance(
            messages,
            list,
        ):
            raise TypeError(
                "messages must be a list."
            )

        if not messages:
            raise ValueError(
                "messages cannot be empty."
            )

        for index, message in enumerate(
            messages
        ):

            if not isinstance(
                message,
                dict,
            ):
                raise TypeError(
                    f"messages[{index}] must be "
                    "a dictionary."
                )

            role = message.get(
                "role"
            )

            if not isinstance(
                role,
                str,
            ):
                raise TypeError(
                    f"messages[{index}].role must "
                    "be a string."
                )

            if not role.strip():
                raise ValueError(
                    f"messages[{index}].role cannot "
                    "be empty."
                )

            if "content" not in message:
                raise ValueError(
                    f"messages[{index}] is missing "
                    "'content'."
                )

            content = message["content"]

            if content is not None and not isinstance(
                content,
                (str, list),
            ):
                raise TypeError(
                    f"messages[{index}].content must "
                    "be a string, list, or None."
                )

    @staticmethod
    def validate_texts(
        texts: list[str],
    ) -> None:
        """
        Validate embedding input.
        """

        if not isinstance(
            texts,
            list,
        ):
            raise TypeError(
                "texts must be a list."
            )

        if not texts:
            raise ValueError(
                "texts cannot be empty."
            )

        for index, text in enumerate(
            texts
        ):

            if not isinstance(
                text,
                str,
            ):
                raise TypeError(
                    f"texts[{index}] must be "
                    "a string."
                )

            if not text.strip():
                raise ValueError(
                    f"texts[{index}] cannot be empty."
                )

    @staticmethod
    def validate_generation_parameters(
        *,
        temperature: float,
        max_tokens: int,
    ) -> None:
        """
        Validate generation parameters.
        """

        if isinstance(
            temperature,
            bool,
        ) or not isinstance(
            temperature,
            (int, float),
        ):
            raise TypeError(
                "temperature must be numeric."
            )

        if temperature < 0:
            raise ValueError(
                "temperature cannot be negative."
            )

        if isinstance(
            max_tokens,
            bool,
        ) or not isinstance(
            max_tokens,
            int,
        ):
            raise TypeError(
                "max_tokens must be an integer."
            )

        if max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than zero."
            )

    # ======================================================================
    # REPRESENTATION
    # ======================================================================

    def __repr__(self) -> str:
        """
        Safe provider representation.

        Never exposes API credentials.
        """

        return (
            f"{self.__class__.__name__}("
            f"provider={self.provider_name!r}, "
            f"model={self.model!r}"
            ")"
        )