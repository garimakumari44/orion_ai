"""
app/llm/manager.py

Canonical Application-Facing LLM Interface
==========================================

Application code communicates with LLMs ONLY through LLMManager.

Architecture:

    Agent / Planner / Service
              |
              v
         LLMManager
              |
              +--> ContextBudget
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
              v
           LLM API


Fallback:

    Provider execution failure
              |
              v
       Error Classification
              |
              v
       FallbackStrategy
              |
              v
       next provider/model


Design rules
------------

1. Application code must use LLMManager.
2. LLMManager never performs HTTP requests directly.
3. Provider implementations are owned by ProviderRouter/factory.
4. Model selection is owned by ModelRouter.
5. Provider resolution is owned by ProviderRouter.
6. Fallback selection is owned by FallbackStrategy.
7. LLMManager owns execution policy and error classification.
8. ContextBudget is applied before routing/execution.
9. Embeddings use ProviderRouter and participate in fallback.
10. Streaming never retries after partial output has already been emitted.
11. Arbitrary internal kwargs are NEVER forwarded directly to providers.
12. Provider-facing chat kwargs are explicitly allowlisted.
"""

from __future__ import annotations

import logging
from typing import Any, Iterator, Optional

from .constants import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROVIDER,
    DEFAULT_TEMPERATURE,
    OPENROUTER,
    TASK_FALLBACK_MODELS,
)

from .context import (
    ContextBudget,
    ContextBudgetResult,
    DEFAULT_CONTEXT_BUDGET,
)

from .providers.base import (
    BaseLLMProvider,
)

from .routing.fallback import (
    FallbackStrategy,
    FallbackTarget,
)

from .routing.model_router import (
    ModelRouter,
    RouteDecision,
)

from .routing.provider_router import (
    ProviderRouter,
)


logger = logging.getLogger(__name__)


# ============================================================================
# LLM MANAGER
# ============================================================================


class LLMManager:
    """
    Canonical application-facing LLM interface.

    LLMManager owns application-level execution policy.

    Provider-specific request parameters are explicitly filtered before
    reaching BaseLLMProvider implementations.

    This is important because provider implementations may eventually call
    OpenAI/OpenRouter-compatible SDKs whose ``create()`` methods reject
    arbitrary internal application kwargs.
    """

    # =========================================================================
    # PROVIDER-FACING CHAT PARAMETER ALLOWLIST
    # =========================================================================

    _ALLOWED_CHAT_PROVIDER_KWARGS = frozenset(
        {
            # Sampling / generation
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "seed",
            "stop",

            # Structured output
            "response_format",

            # Tool / function calling
            "tools",
            "tool_choice",
            "parallel_tool_calls",

            # OpenAI-compatible optional parameters
            "logit_bias",
            "user",

            # Reasoning-capable providers / OpenRouter-compatible APIs
            "reasoning",

            # Optional modalities / response controls supported by some
            # OpenAI-compatible providers.
            "modalities",
            "audio",

            # OpenRouter/provider routing controls.
            #
            # These are provider-facing request parameters, not internal
            # LLMManager routing arguments.
            "provider",
        }
    )

    # Internal/application kwargs that must NEVER be forwarded to providers.
    #
    # This is primarily defensive documentation. The actual protection is
    # provided by the allowlist above.
    _INTERNAL_KWARGS = frozenset(
        {
            "task",
            "provider_router",
            "model_router",
            "context_budget",
            "fallback_strategy",
            "route_decision",
            "decision",
            "debug",
            "metadata",
            "request_context",
            "trace_context",
            "internal",
        }
    )

    # ------------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------------

    def __init__(
        self,
        model_router: ModelRouter,
        provider_router: ProviderRouter,
        *,
        context_budget: ContextBudget | None = None,
        fallback_strategy: FallbackStrategy | None = None,
    ) -> None:

        if not isinstance(model_router, ModelRouter):
            raise TypeError(
                "model_router must be a ModelRouter."
            )

        if not isinstance(provider_router, ProviderRouter):
            raise TypeError(
                "provider_router must be a ProviderRouter."
            )

        if (
            context_budget is not None
            and not isinstance(context_budget, ContextBudget)
        ):
            raise TypeError(
                "context_budget must be a ContextBudget instance or None."
            )

        if (
            fallback_strategy is not None
            and not isinstance(fallback_strategy, FallbackStrategy)
        ):
            raise TypeError(
                "fallback_strategy must be a FallbackStrategy instance or None."
            )

        self._model_router = model_router
        self._provider_router = provider_router

        self._context_budget = (
            context_budget
            if context_budget is not None
            else ContextBudget(
                max_context_tokens=DEFAULT_CONTEXT_BUDGET
            )
        )

        self._fallback_strategy = (
            fallback_strategy
            if fallback_strategy is not None
            else FallbackStrategy()
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def context_budget(self) -> ContextBudget:
        return self._context_budget

    @property
    def model_router(self) -> ModelRouter:
        return self._model_router

    @property
    def provider_router(self) -> ProviderRouter:
        return self._provider_router

    @property
    def fallback_strategy(self) -> FallbackStrategy:
        return self._fallback_strategy

    # =========================================================================
    # PROVIDER KWARG HARDENING
    # =========================================================================

    @classmethod
    def _build_chat_provider_kwargs(
        cls,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build the ONLY kwargs allowed to cross the provider boundary.

        Application code may pass additional kwargs into LLMManager.chat()
        or stream(), but those kwargs are NOT forwarded blindly.

        This prevents internal application arguments from reaching an
        OpenAI/OpenRouter SDK ``Completions.create()`` call.

        Example:

            manager.chat(
                messages=messages,
                task="research",
                temperature=0.2,
                internal_trace_id="abc",
                top_p=0.9,
            )

        Provider receives:

            {
                "top_p": 0.9
            }

        and does NOT receive:

            task
            internal_trace_id
        """

        if not kwargs:
            return {}

        provider_kwargs: dict[str, Any] = {}

        ignored: list[str] = []

        for key, value in kwargs.items():

            if key in cls._ALLOWED_CHAT_PROVIDER_KWARGS:
                provider_kwargs[key] = value

            else:
                ignored.append(key)

        if ignored:
            logger.warning(
                (
                    "Ignoring unsupported/internal LLM provider kwargs | "
                    "kwargs=%s"
                ),
                sorted(ignored),
            )

        return provider_kwargs

    # =========================================================================
    # GENERATE
    # =========================================================================

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        task: str = "chat",
        **kwargs: Any,
    ) -> str:
        """
        Generate a response from a single user prompt.

        This is a convenience wrapper around chat().
        """

        self._validate_prompt(prompt)

        if (
            system_prompt is not None
            and not isinstance(system_prompt, str)
        ):
            raise TypeError(
                "system_prompt must be a string or None."
            )

        self._validate_generation_parameters(
            temperature=temperature,
            max_tokens=max_tokens,
        )

        messages: list[dict[str, Any]] = []

        if (
            system_prompt is not None
            and system_prompt.strip()
        ):
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
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            provider=provider,
            task=task,
            **kwargs,
        )

    # =========================================================================
    # CHAT
    # =========================================================================

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        task: str = "chat",
        **kwargs: Any,
    ) -> str:
        """
        Execute a normal non-streaming chat request.

        Important:

        ``kwargs`` belongs to the application-facing API.

        It is NOT forwarded directly to providers.

        Only parameters explicitly approved by
        ``_ALLOWED_CHAT_PROVIDER_KWARGS`` can cross the provider boundary.
        """

        self._validate_messages(messages)

        self._validate_generation_parameters(
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self._validate_task(task)

        result = (
            self._context_budget.prepare_messages_with_result(
                messages,
                reserved_output_tokens=max_tokens,
            )
        )

        self._log_context_budget(
            task=task,
            model=model,
            result=result,
            max_tokens=max_tokens,
        )

        decision = self._route(
            task=task,
            prepared_messages=result.messages,
            max_tokens=max_tokens,
            model=model,
            provider=provider,
        )

        provider_kwargs = (
            self._build_chat_provider_kwargs(kwargs)
        )

        return self._execute_chat_with_fallback(
            decision=decision,
            messages=result.messages,
            temperature=temperature,
            max_tokens=max_tokens,
            task=task,
            provider_kwargs=provider_kwargs,
        )

    # =========================================================================
    # STREAM
    # =========================================================================

    def stream(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        task: str = "chat",
        **kwargs: Any,
    ) -> Iterator[str]:
        """
        Execute a streaming chat request.

        If the provider fails BEFORE yielding any content, fallback is safe.

        If the provider has already emitted content and subsequently fails,
        automatic fallback is NOT attempted.
        """

        self._validate_messages(messages)

        self._validate_generation_parameters(
            temperature=temperature,
            max_tokens=max_tokens,
        )

        self._validate_task(task)

        result = (
            self._context_budget.prepare_messages_with_result(
                messages,
                reserved_output_tokens=max_tokens,
            )
        )

        self._log_context_budget(
            task=task,
            model=model,
            result=result,
            max_tokens=max_tokens,
        )

        decision = self._route(
            task=task,
            prepared_messages=result.messages,
            max_tokens=max_tokens,
            model=model,
            provider=provider,
        )

        provider_kwargs = (
            self._build_chat_provider_kwargs(kwargs)
        )

        yield from self._execute_stream_with_fallback(
            decision=decision,
            messages=result.messages,
            temperature=temperature,
            max_tokens=max_tokens,
            task=task,
            provider_kwargs=provider_kwargs,
        )

    # =========================================================================
    # EMBEDDINGS
    # =========================================================================

    def embeddings(
        self,
        texts: list[str],
        *,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        task: str = "embedding",
        **kwargs: Any,
    ) -> list[list[float]]:
        """
        Generate embeddings.

        Embeddings intentionally do not use ModelRouter.

        Provider resolution still goes through ProviderRouter.

        NOTE:

        Embedding kwargs are intentionally passed through here because the
        embedding provider contract may differ from chat.

        If your embedding provider also forwards kwargs directly into an SDK,
        it should receive the same allowlist treatment in a separate helper.
        """

        self._validate_texts(texts)
        self._validate_task(task)

        selected_provider = (
            provider
            or DEFAULT_PROVIDER
        )

        selected_model = model

        state = self._fallback_strategy.reset()

        initial_target = FallbackTarget(
            provider=selected_provider,
            model=selected_model or "",
        )

        state.add_attempt(
            initial_target,
            "Initial embedding provider attempt",
        )

        credit_exhausted = False
        last_exception: Optional[Exception] = None

        # ---------------------------------------------------------------------
        # Initial embedding attempt
        # ---------------------------------------------------------------------

        try:
            client = self._provider_router.get_client(
                provider=selected_provider,
                model=selected_model,
            )

            if not isinstance(client, BaseLLMProvider):
                raise RuntimeError(
                    "ProviderRouter returned an invalid provider "
                    "for embeddings."
                )

            logger.info(
                (
                    "LLM embedding attempt | "
                    "provider=%s | "
                    "model=%s | "
                    "task=%s | "
                    "texts=%d | "
                    "attempt=1"
                ),
                selected_provider,
                selected_model,
                task,
                len(texts),
            )

            return client.embeddings(
                texts=texts,
                model=selected_model,
                **kwargs,
            )

        except Exception as exc:

            last_exception = exc

            status_code = self._extract_status_code(exc)

            credit_exhausted = self._is_credit_exhaustion(exc)

            logger.warning(
                (
                    "LLM embedding execution failed | "
                    "provider=%s | "
                    "model=%s | "
                    "task=%s | "
                    "status=%s | "
                    "credit_exhausted=%s | "
                    "error=%s"
                ),
                selected_provider,
                selected_model,
                task,
                status_code,
                credit_exhausted,
                exc,
            )

            if not self._is_retryable_llm_error(exc):
                raise RuntimeError(
                    (
                        "Embedding execution failed with a "
                        f"non-retryable error (status={status_code}). "
                        f"Provider={selected_provider}, "
                        f"model={selected_model}."
                    )
                ) from exc

        # ---------------------------------------------------------------------
        # Embedding fallback
        # ---------------------------------------------------------------------

        while not self._fallback_strategy.exhausted(
            state,
            providers=self._registered_provider_map(),
        ):

            target = self._fallback_strategy.next_target(
                state,
                providers=self._registered_provider_map(),
            )

            if target is None:
                break

            if (
                target.provider == selected_provider
                and target.model == (selected_model or "")
            ):
                state.add_attempt(
                    target,
                    "Skipped: duplicate initial embedding target",
                )
                continue

            if credit_exhausted:
                if (
                    target.provider == OPENROUTER
                    and not self._is_free_model(target.model)
                ):
                    state.add_attempt(
                        target,
                        (
                            "Skipped: account credit exhaustion "
                            "and model is not explicitly free"
                        ),
                    )

                    logger.info(
                        (
                            "Skipping paid embedding fallback after "
                            "credit exhaustion | "
                            "provider=%s | "
                            "model=%s"
                        ),
                        target.provider,
                        target.model,
                    )

                    continue

            try:

                client = self._provider_router.get_client(
                    provider=target.provider,
                    model=target.model or None,
                )

                if not isinstance(client, BaseLLMProvider):
                    raise RuntimeError(
                        "ProviderRouter returned an invalid provider "
                        "for embedding fallback."
                    )

                logger.warning(
                    (
                        "LLM embedding fallback attempt | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s | "
                        "attempt=%d"
                    ),
                    target.provider,
                    target.model,
                    task,
                    len(state.attempted) + 1,
                )

                result = client.embeddings(
                    texts=texts,
                    model=target.model or None,
                    **kwargs,
                )

                logger.info(
                    (
                        "LLM embedding fallback succeeded | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                )

                return result

            except Exception as exc:

                last_exception = exc

                status_code = self._extract_status_code(exc)

                current_credit_exhaustion = (
                    self._is_credit_exhaustion(exc)
                )

                if current_credit_exhaustion:
                    credit_exhausted = True

                state.add_attempt(
                    target,
                    str(exc),
                )

                logger.warning(
                    (
                        "LLM embedding fallback failed | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s | "
                        "status=%s | "
                        "credit_exhausted=%s | "
                        "error=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                    status_code,
                    current_credit_exhaustion,
                    exc,
                )

                if not self._is_retryable_llm_error(exc):
                    break

        attempted = self._format_attempts(state)

        if credit_exhausted:
            message = (
                "LLM embedding execution failed because the available "
                "provider credit budget was insufficient. "
                "Free fallback models were exhausted or unavailable. "
            )
        else:
            message = (
                "All retryable LLM embedding attempts failed. "
            )

        raise RuntimeError(
            message
            + f"Attempted: {attempted}"
        ) from last_exception

    # =========================================================================
    # HEALTH
    # =========================================================================

    def health_check(self) -> bool:
        """Return True when at least one provider is available."""

        try:
            return bool(
                self._provider_router.available_providers()
            )

        except Exception:
            logger.exception(
                "LLM provider health check failed."
            )
            return False

    def provider_health(self) -> dict[str, bool]:
        """Return availability state for all registered providers."""

        result: dict[str, bool] = {}

        try:
            registered = (
                self._provider_router.registered_providers()
            )

            for provider_name in registered:
                try:
                    result[provider_name] = bool(
                        self._provider_router.is_available(
                            provider_name
                        )
                    )
                except Exception:
                    logger.exception(
                        (
                            "Provider availability check failed | "
                            "provider=%s"
                        ),
                        provider_name,
                    )
                    result[provider_name] = False

        except Exception:
            logger.exception(
                "Failed to inspect registered LLM providers."
            )

        return result

    # =========================================================================
    # CONTEXT
    # =========================================================================

    def estimate_prompt_tokens(
        self,
        prompt: str,
    ) -> int:
        return self._context_budget.estimate_tokens(prompt)

    def prepare_prompt(
        self,
        prompt: str,
        *,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> ContextBudgetResult:

        return self._context_budget.prepare_prompt(
            prompt,
            reserved_output_tokens=max_tokens,
        )

    def prepare_messages(
        self,
        messages: list[dict[str, Any]],
        *,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> list[dict[str, Any]]:

        return self._context_budget.prepare_messages(
            messages,
            reserved_output_tokens=max_tokens,
        )

    # =========================================================================
    # ROUTING
    # =========================================================================

    def route(
        self,
        *,
        task: str = "chat",
        prompt: str = "",
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> RouteDecision:
        """Public routing inspection API."""

        if not isinstance(prompt, str):
            raise TypeError(
                "prompt must be a string."
            )

        self._validate_task(task)

        self._validate_generation_parameters(
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=max_tokens,
        )

        prepared_prompt = prompt

        if prompt.strip():
            prepared_prompt = (
                self._context_budget.prepare_prompt(
                    prompt,
                    reserved_output_tokens=max_tokens,
                ).content
            )

        decision = self._model_router.route(
            task=task,
            prompt=prepared_prompt,
            max_tokens=max_tokens,
            prefer_provider=provider,
            prefer_model=model,
        )

        self._validate_route_decision(decision)

        return decision

    # =========================================================================
    # INTERNAL ROUTING
    # =========================================================================

    def _route(
        self,
        *,
        task: str,
        prepared_messages: list[dict[str, Any]],
        max_tokens: int,
        model: Optional[str],
        provider: Optional[str],
    ) -> RouteDecision:

        self._validate_task(task)

        routing_prompt = self._build_routing_prompt(
            prepared_messages
        )

        decision = self._model_router.route(
            task=task,
            prompt=routing_prompt,
            max_tokens=max_tokens,
            prefer_provider=provider,
            prefer_model=model,
        )

        self._validate_route_decision(decision)

        logger.info(
            (
                "LLM route selected | "
                "task=%s | "
                "provider=%s | "
                "model=%s | "
                "reason=%s"
            ),
            task,
            decision.provider,
            decision.model,
            getattr(
                decision,
                "reason",
                None,
            ),
        )

        return decision

    # =========================================================================
    # ERROR CLASSIFICATION
    # =========================================================================

    @staticmethod
    def _extract_status_code(
        exc: BaseException,
    ) -> Optional[int]:

        status_code = getattr(
            exc,
            "status_code",
            None,
        )

        if isinstance(status_code, int):
            return status_code

        response = getattr(
            exc,
            "response",
            None,
        )

        if response is not None:

            response_status = getattr(
                response,
                "status_code",
                None,
            )

            if isinstance(response_status, int):
                return response_status

        code = getattr(
            exc,
            "code",
            None,
        )

        if isinstance(code, int):
            return code

        if (
            isinstance(code, str)
            and code.strip().isdigit()
        ):
            return int(code.strip())

        body = getattr(
            exc,
            "body",
            None,
        )

        if isinstance(body, dict):

            body_error = body.get("error")

            if isinstance(body_error, dict):

                body_code = body_error.get("code")

                if isinstance(body_code, int):
                    return body_code

                if (
                    isinstance(body_code, str)
                    and body_code.strip().isdigit()
                ):
                    return int(body_code.strip())

        response_data = getattr(
            response,
            "json",
            None,
        )

        if callable(response_data):

            try:
                payload = response_data()

                if isinstance(payload, dict):

                    error_payload = payload.get("error")

                    if isinstance(error_payload, dict):

                        payload_code = error_payload.get(
                            "code"
                        )

                        if isinstance(
                            payload_code,
                            int,
                        ):
                            return payload_code

                        if (
                            isinstance(
                                payload_code,
                                str,
                            )
                            and payload_code.strip().isdigit()
                        ):
                            return int(
                                payload_code.strip()
                            )

            except Exception:
                pass

        text = str(exc).lower()

        known_codes = (
            400,
            401,
            402,
            403,
            404,
            408,
            409,
            429,
            500,
            502,
            503,
            504,
        )

        for code_value in known_codes:

            patterns = (
                f"code: {code_value}",
                f"code={code_value}",
                f"code {code_value}",
                f'"code": {code_value}',
                f'"status": {code_value}',
                f'"status_code": {code_value}',
                f"status code {code_value}",
                f"status_code={code_value}",
                f"http {code_value}",
                f"http/{code_value}",
            )

            if any(
                pattern in text
                for pattern in patterns
            ):
                return code_value

        return None

    @classmethod
    def _is_credit_exhaustion(
        cls,
        exc: BaseException,
    ) -> bool:

        if cls._extract_status_code(exc) == 402:
            return True

        text = str(exc).lower()

        markers = (
            "requires more credits",
            "insufficient credits",
            "insufficient credit",
            "can only afford",
            "openrouter_credits",
            "payment required",
            "credit balance",
            "credits exhausted",
            "credit exhausted",
            "out of credits",
            "not enough credits",
            "billing limit",
            "spending limit",
            "quota exceeded",
            "quota has been exceeded",
        )

        return any(
            marker in text
            for marker in markers
        )

    @classmethod
    def _is_retryable_llm_error(
        cls,
        exc: BaseException,
    ) -> bool:

        status_code = cls._extract_status_code(exc)

        if status_code in {
            408,
            429,
            500,
            502,
            503,
            504,
        }:
            return True

        if status_code == 402:
            return True

        if status_code in {
            400,
            401,
            403,
            404,
        }:
            return False

        text = str(exc).lower()

        non_retryable_markers = (
            "invalid request",
            "invalid parameter",
            "invalid model",
            "authentication failed",
            "unauthorized",
            "forbidden",
            "permission denied",
            "not found",
            "model not found",
            "bad request",
            "malformed request",
        )

        if any(
            marker in text
            for marker in non_retryable_markers
        ):
            return False

        retryable_markers = (
            "timeout",
            "timed out",
            "read timeout",
            "connect timeout",
            "connection reset",
            "connection refused",
            "connection aborted",
            "connection error",
            "temporarily unavailable",
            "temporarily rate-limited",
            "rate limit",
            "rate-limited",
            "too many requests",
            "service unavailable",
            "server error",
            "upstream error",
            "gateway error",
            "bad gateway",
            "gateway timeout",
            "overloaded",
            "temporarily overloaded",
            "internal server error",
            "try again later",
        )

        if any(
            marker in text
            for marker in retryable_markers
        ):
            return True

        return True

    # =========================================================================
    # MODEL POLICY
    # =========================================================================

    @staticmethod
    def _is_free_model(
        model: str,
    ) -> bool:

        return (
            isinstance(model, str)
            and model.strip().endswith(":free")
        )

    @staticmethod
    def _task_allows_model(
        *,
        task: str,
        provider: str,
        model: str,
    ) -> bool:

        if provider != OPENROUTER:
            return True

        candidates = TASK_FALLBACK_MODELS.get(task)

        if not candidates:
            return True

        return model in candidates

    # =========================================================================
    # CHAT EXECUTION + FALLBACK
    # =========================================================================

    def _execute_chat_with_fallback(
        self,
        *,
        decision: RouteDecision,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        task: str = "chat",
        provider_kwargs: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Execute a normal chat request with fallback.

        ``provider_kwargs`` has already been sanitized by
        ``_build_chat_provider_kwargs()``.

        No arbitrary kwargs are accepted here.
        """

        provider_kwargs = dict(
            provider_kwargs or {}
        )

        state = self._fallback_strategy.reset()

        initial_target = FallbackTarget(
            provider=decision.provider,
            model=decision.model,
        )

        state.add_attempt(
            initial_target,
            "Initial routed attempt",
        )

        last_exception: Optional[Exception] = None

        credit_exhausted = False

        # ---------------------------------------------------------------------
        # INITIAL ATTEMPT
        # ---------------------------------------------------------------------

        try:

            client = self._resolve_provider(
                decision
            )

            logger.info(
                (
                    "LLM execution attempt | "
                    "provider=%s | "
                    "model=%s | "
                    "task=%s | "
                    "attempt=1"
                ),
                decision.provider,
                decision.model,
                task,
            )

            result = client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=decision.model,
                **provider_kwargs,
            )

            return self._normalize_chat_result(
                result
            )

        except Exception as initial_exc:

            last_exception = initial_exc

            status_code = self._extract_status_code(
                initial_exc
            )

            credit_exhausted = (
                self._is_credit_exhaustion(
                    initial_exc
                )
            )

            logger.warning(
                (
                    "LLM execution failed | "
                    "provider=%s | "
                    "model=%s | "
                    "task=%s | "
                    "status=%s | "
                    "credit_exhausted=%s | "
                    "error=%s"
                ),
                decision.provider,
                decision.model,
                task,
                status_code,
                credit_exhausted,
                initial_exc,
            )

            if not self._is_retryable_llm_error(
                initial_exc
            ):
                raise RuntimeError(
                    (
                        "LLM execution failed with a "
                        "non-retryable error "
                        f"(status={status_code}). "
                        f"Provider={decision.provider}, "
                        f"model={decision.model}."
                    )
                ) from initial_exc

        # ---------------------------------------------------------------------
        # FALLBACK LOOP
        # ---------------------------------------------------------------------

        while not self._fallback_strategy.exhausted(
            state,
            providers=self._registered_provider_map(),
        ):

            target = (
                self._fallback_strategy.next_target(
                    state,
                    providers=self._registered_provider_map(),
                )
            )

            if target is None:
                break

            if self._target_already_attempted(
                state,
                target,
            ):
                state.add_attempt(
                    target,
                    "Skipped: duplicate fallback target",
                )
                continue

            if not self._task_allows_model(
                task=task,
                provider=target.provider,
                model=target.model,
            ):

                logger.debug(
                    (
                        "Skipping task-incompatible fallback | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                )

                state.add_attempt(
                    target,
                    (
                        "Skipped: model is not configured "
                        f"for task '{task}'"
                    ),
                )

                continue

            if credit_exhausted:

                if (
                    target.provider == OPENROUTER
                    and not self._is_free_model(
                        target.model
                    )
                ):

                    logger.info(
                        (
                            "Skipping paid fallback after "
                            "credit exhaustion | "
                            "provider=%s | "
                            "model=%s"
                        ),
                        target.provider,
                        target.model,
                    )

                    state.add_attempt(
                        target,
                        (
                            "Skipped: account credit exhaustion "
                            "and model is not explicitly free"
                        ),
                    )

                    continue

            try:

                fallback_decision = RouteDecision(
                    provider=target.provider,
                    model=target.model,
                    reason=(
                        "Fallback after "
                        "retryable provider failure"
                    ),
                )

                client = self._resolve_provider(
                    fallback_decision
                )

                logger.warning(
                    (
                        "LLM fallback attempt | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s | "
                        "attempt=%d"
                    ),
                    target.provider,
                    target.model,
                    task,
                    len(state.attempted) + 1,
                )

                result = client.chat(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=target.model,
                    **provider_kwargs,
                )

                logger.info(
                    (
                        "LLM fallback succeeded | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                )

                return self._normalize_chat_result(
                    result
                )

            except Exception as exc:

                last_exception = exc

                status_code = self._extract_status_code(
                    exc
                )

                current_credit_exhaustion = (
                    self._is_credit_exhaustion(
                        exc
                    )
                )

                if current_credit_exhaustion:
                    credit_exhausted = True

                state.add_attempt(
                    target,
                    str(exc),
                )

                logger.warning(
                    (
                        "LLM fallback failed | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s | "
                        "status=%s | "
                        "credit_exhausted=%s | "
                        "error=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                    status_code,
                    current_credit_exhaustion,
                    exc,
                )

                if not self._is_retryable_llm_error(
                    exc
                ):
                    break

        attempted = self._format_attempts(
            state
        )

        if credit_exhausted:

            message = (
                "LLM execution failed because the available "
                "provider credit budget was insufficient. "
                "Free fallback models were exhausted or unavailable. "
            )

        else:

            message = (
                "All retryable LLM execution attempts failed. "
            )

        raise RuntimeError(
            message
            + f"Attempted: {attempted}"
        ) from last_exception

    # =========================================================================
    # STREAM EXECUTION + FALLBACK
    # =========================================================================

    def _execute_stream_with_fallback(
        self,
        *,
        decision: RouteDecision,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        task: str = "chat",
        provider_kwargs: Optional[dict[str, Any]] = None,
    ) -> Iterator[str]:
        """
        Execute a streaming request with safe fallback semantics.

        Fallback is only safe before the first emitted chunk.
        """

        provider_kwargs = dict(
            provider_kwargs or {}
        )

        state = self._fallback_strategy.reset()

        initial_target = FallbackTarget(
            provider=decision.provider,
            model=decision.model,
        )

        state.add_attempt(
            initial_target,
            "Initial routed stream attempt",
        )

        last_exception: Optional[Exception] = None

        credit_exhausted = False

        emitted_any = False

        # ---------------------------------------------------------------------
        # INITIAL STREAM
        # ---------------------------------------------------------------------

        try:

            client = self._resolve_provider(
                decision
            )

            logger.info(
                (
                    "LLM stream attempt | "
                    "provider=%s | "
                    "model=%s | "
                    "task=%s | "
                    "attempt=1"
                ),
                decision.provider,
                decision.model,
                task,
            )

            for chunk in client.stream(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=decision.model,
                **provider_kwargs,
            ):

                if chunk is not None:
                    emitted_any = True
                    yield str(chunk)

            return

        except Exception as initial_exc:

            last_exception = initial_exc

            status_code = self._extract_status_code(
                initial_exc
            )

            credit_exhausted = (
                self._is_credit_exhaustion(
                    initial_exc
                )
            )

            logger.warning(
                (
                    "LLM stream execution failed | "
                    "provider=%s | "
                    "model=%s | "
                    "task=%s | "
                    "status=%s | "
                    "credit_exhausted=%s | "
                    "emitted_any=%s | "
                    "error=%s"
                ),
                decision.provider,
                decision.model,
                task,
                status_code,
                credit_exhausted,
                emitted_any,
                initial_exc,
            )

            if emitted_any:

                raise RuntimeError(
                    (
                        "LLM stream failed after partial output "
                        "had already been emitted. "
                        "Automatic fallback was disabled to prevent "
                        "duplicate/corrupted streamed output. "
                        f"Provider={decision.provider}, "
                        f"model={decision.model}."
                    )
                ) from initial_exc

            if not self._is_retryable_llm_error(
                initial_exc
            ):

                raise RuntimeError(
                    (
                        "LLM stream execution failed with "
                        "a non-retryable error "
                        f"(status={status_code}). "
                        f"Provider={decision.provider}, "
                        f"model={decision.model}."
                    )
                ) from initial_exc

        # ---------------------------------------------------------------------
        # STREAM FALLBACK
        # ---------------------------------------------------------------------

        while not self._fallback_strategy.exhausted(
            state,
            providers=self._registered_provider_map(),
        ):

            target = (
                self._fallback_strategy.next_target(
                    state,
                    providers=self._registered_provider_map(),
                )
            )

            if target is None:
                break

            if self._target_already_attempted(
                state,
                target,
            ):
                state.add_attempt(
                    target,
                    "Skipped: duplicate stream fallback target",
                )
                continue

            if not self._task_allows_model(
                task=task,
                provider=target.provider,
                model=target.model,
            ):

                state.add_attempt(
                    target,
                    (
                        "Skipped: model is not configured "
                        f"for task '{task}'"
                    ),
                )

                logger.debug(
                    (
                        "Skipping task-incompatible stream fallback | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                )

                continue

            if credit_exhausted:

                if (
                    target.provider == OPENROUTER
                    and not self._is_free_model(
                        target.model
                    )
                ):

                    state.add_attempt(
                        target,
                        (
                            "Skipped: account credit exhaustion "
                            "and model is not explicitly free"
                        ),
                    )

                    logger.info(
                        (
                            "Skipping paid stream fallback after "
                            "credit exhaustion | "
                            "provider=%s | "
                            "model=%s"
                        ),
                        target.provider,
                        target.model,
                    )

                    continue

            fallback_emitted_any = False

            try:

                fallback_decision = RouteDecision(
                    provider=target.provider,
                    model=target.model,
                    reason=(
                        "Fallback after "
                        "stream provider failure"
                    ),
                )

                client = self._resolve_provider(
                    fallback_decision
                )

                logger.warning(
                    (
                        "LLM stream fallback attempt | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s | "
                        "attempt=%d"
                    ),
                    target.provider,
                    target.model,
                    task,
                    len(state.attempted) + 1,
                )

                for chunk in client.stream(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=target.model,
                    **provider_kwargs,
                ):

                    if chunk is not None:
                        fallback_emitted_any = True
                        yield str(chunk)

                logger.info(
                    (
                        "LLM stream fallback succeeded | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                )

                return

            except Exception as exc:

                last_exception = exc

                status_code = self._extract_status_code(
                    exc
                )

                current_credit_exhaustion = (
                    self._is_credit_exhaustion(exc)
                )

                if current_credit_exhaustion:
                    credit_exhausted = True

                state.add_attempt(
                    target,
                    str(exc),
                )

                logger.warning(
                    (
                        "LLM stream fallback failed | "
                        "provider=%s | "
                        "model=%s | "
                        "task=%s | "
                        "status=%s | "
                        "credit_exhausted=%s | "
                        "emitted_any=%s | "
                        "error=%s"
                    ),
                    target.provider,
                    target.model,
                    task,
                    status_code,
                    current_credit_exhaustion,
                    fallback_emitted_any,
                    exc,
                )

                if fallback_emitted_any:

                    raise RuntimeError(
                        (
                            "LLM stream fallback provider failed "
                            "after partial output had already been "
                            "emitted. Further fallback was disabled "
                            "to prevent duplicate/corrupted output. "
                            f"Provider={target.provider}, "
                            f"model={target.model}."
                        )
                    ) from exc

                if not self._is_retryable_llm_error(
                    exc
                ):
                    break

        attempted = self._format_attempts(
            state
        )

        if credit_exhausted:

            message = (
                "LLM stream execution failed because the available "
                "provider credit budget was insufficient. "
                "Free fallback models were exhausted or unavailable. "
            )

        else:

            message = (
                "All retryable LLM stream attempts failed. "
            )

        raise RuntimeError(
            message
            + f"Attempted: {attempted}"
        ) from last_exception

    # =========================================================================
    # PROVIDER REGISTRY
    # =========================================================================

    def _registered_provider_map(
        self,
    ) -> dict[str, BaseLLMProvider]:

        try:
            providers = self._provider_router.providers()

        except Exception as exc:

            raise RuntimeError(
                "ProviderRouter failed to expose registered providers."
            ) from exc

        if not isinstance(providers, dict):
            try:
                providers = dict(providers)
            except Exception as exc:
                raise RuntimeError(
                    (
                        "ProviderRouter.providers() must return "
                        "a provider mapping."
                    )
                ) from exc

        result: dict[str, BaseLLMProvider] = {}

        for name, provider in providers.items():

            if isinstance(
                provider,
                BaseLLMProvider,
            ):
                result[str(name)] = provider

        return result

    # =========================================================================
    # PROVIDER RESOLUTION
    # =========================================================================

    def _resolve_provider(
        self,
        decision: RouteDecision,
    ) -> BaseLLMProvider:

        self._validate_route_decision(
            decision
        )

        try:

            client = (
                self._provider_router.get_client(
                    provider=decision.provider,
                    model=decision.model,
                )
            )

        except Exception as exc:

            raise RuntimeError(
                (
                    "Failed to resolve LLM provider "
                    f"'{decision.provider}' "
                    f"for model '{decision.model}'."
                )
            ) from exc

        if not isinstance(
            client,
            BaseLLMProvider,
        ):
            raise RuntimeError(
                (
                    "ProviderRouter returned an invalid "
                    "LLM provider."
                )
            )

        return client

    # =========================================================================
    # ROUTE VALIDATION
    # =========================================================================

    @staticmethod
    def _validate_route_decision(
        decision: RouteDecision,
    ) -> None:

        if not isinstance(
            decision,
            RouteDecision,
        ):
            raise TypeError(
                (
                    "ModelRouter.route() must return "
                    "a RouteDecision."
                )
            )

        if not isinstance(
            decision.provider,
            str,
        ):
            raise TypeError(
                "RouteDecision.provider must be a string."
            )

        if not decision.provider.strip():
            raise RuntimeError(
                "ModelRouter returned an empty provider."
            )

        if not isinstance(
            decision.model,
            str,
        ):
            raise TypeError(
                "RouteDecision.model must be a string."
            )

        if not decision.model.strip():
            raise RuntimeError(
                "ModelRouter returned an empty model."
            )

    # =========================================================================
    # FALLBACK HELPERS
    # =========================================================================

    @staticmethod
    def _target_already_attempted(
        state: Any,
        target: FallbackTarget,
    ) -> bool:

        attempted = getattr(
            state,
            "attempted",
            None,
        )

        if not attempted:
            return False

        for existing in attempted:

            if (
                getattr(existing, "provider", None)
                == target.provider
                and getattr(existing, "model", None)
                == target.model
            ):
                return True

        return False

    @staticmethod
    def _format_attempts(
        state: Any,
    ) -> str:

        attempted = getattr(
            state,
            "attempted",
            [],
        )

        formatted: list[str] = []

        for target in attempted:

            provider = getattr(
                target,
                "provider",
                "unknown",
            )

            model = getattr(
                target,
                "model",
                "unknown",
            )

            formatted.append(
                f"{provider}/{model}"
            )

        return ", ".join(
            formatted
        )

    # =========================================================================
    # RESULT NORMALIZATION
    # =========================================================================

    @staticmethod
    def _normalize_chat_result(
        result: Any,
    ) -> str:

        if result is None:
            raise RuntimeError(
                "LLM provider returned None instead of a response."
            )

        if isinstance(result, str):
            return result

        content = getattr(
            result,
            "content",
            None,
        )

        if isinstance(content, str):
            return content

        choices = getattr(
            result,
            "choices",
            None,
        )

        if choices:

            try:

                first_choice = choices[0]

                message = getattr(
                    first_choice,
                    "message",
                    None,
                )

                if message is not None:

                    content = getattr(
                        message,
                        "content",
                        None,
                    )

                    if isinstance(
                        content,
                        str,
                    ):
                        return content

            except Exception:
                pass

        raise RuntimeError(
            (
                "LLM provider returned an unsupported chat "
                f"response type: {type(result).__name__}."
            )
        )

    # =========================================================================
    # LOGGING
    # =========================================================================

    @staticmethod
    def _log_context_budget(
        *,
        task: str,
        model: Optional[str],
        result: ContextBudgetResult,
        max_tokens: int,
    ) -> None:

        logger.info(
            (
                "LLM context budget | "
                "task=%s | "
                "model=%s | "
                "original_input=%d | "
                "prepared_input=%d | "
                "input_budget=%d | "
                "reserved_output=%d | "
                "total_budget=%d | "
                "truncated=%s | "
                "messages_removed=%d | "
                "chars_removed=%d | "
                "reason=%s"
            ),
            task,
            model or "router-selected",
            result.original_tokens,
            result.prepared_tokens,
            result.budget,
            max_tokens,
            result.budget + max_tokens,
            result.truncated,
            result.messages_removed,
            result.characters_removed,
            result.reason,
        )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @staticmethod
    def _validate_task(
        task: str,
    ) -> None:

        if not isinstance(
            task,
            str,
        ):
            raise TypeError(
                "task must be a string."
            )

        if not task.strip():
            raise ValueError(
                "task cannot be empty."
            )

    @staticmethod
    def _validate_prompt(
        prompt: str,
    ) -> None:

        BaseLLMProvider.validate_prompt(
            prompt
        )

    @staticmethod
    def _validate_messages(
        messages: list[dict[str, Any]],
    ) -> None:

        BaseLLMProvider.validate_messages(
            messages
        )

    @staticmethod
    def _validate_texts(
        texts: list[str],
    ) -> None:

        BaseLLMProvider.validate_texts(
            texts
        )

    @staticmethod
    def _validate_generation_parameters(
        *,
        temperature: float,
        max_tokens: int,
    ) -> None:

        BaseLLMProvider.validate_generation_parameters(
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # =========================================================================
    # ROUTING REPRESENTATION
    # =========================================================================

    @staticmethod
    def _build_routing_prompt(
        messages: list[dict[str, Any]],
    ) -> str:

        parts: list[str] = []

        for message in messages:

            role = str(
                message.get(
                    "role",
                    "user",
                )
            )

            content = message.get(
                "content",
                "",
            )

            if isinstance(
                content,
                str,
            ):

                parts.append(
                    f"{role}: {content}"
                )

            elif isinstance(
                content,
                list,
            ):

                parts.append(
                    f"{role}: [structured content]"
                )

            elif content is None:

                parts.append(
                    f"{role}: "
                )

            else:

                parts.append(
                    f"{role}: {content}"
                )

        return "\n".join(
            parts
        )

    # =========================================================================
    # REPRESENTATION
    # =========================================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "LLMManager("
            f"context_budget="
            f"{self._context_budget!r}, "
            f"model_router="
            f"{self._model_router!r}, "
            f"provider_router="
            f"{self._provider_router!r}, "
            f"fallback_strategy="
            f"{self._fallback_strategy!r}"
            ")"
        )