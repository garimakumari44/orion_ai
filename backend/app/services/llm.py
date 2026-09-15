from __future__ import annotations

import os
import time
import traceback
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIStatusError

load_dotenv()


class LLMService:
    """
    Production-oriented OpenRouter LLM service.

    Responsibilities
    ----------------
    - Model fallback
    - Rate-limit handling
    - OpenRouter 402 handling
    - Retry-after support
    - Response validation
    - Model cooldowns
    - Preventing pointless fallback storms
    """

    MODELS = [
        # Strong primary models
        "meta-llama/llama-3.3-70b-instruct",
        "qwen/qwen3-next-80b-a3b-instruct",

        # Medium / free fallback
        "google/gemma-4-26b-a4b-it:free",

        # Small emergency fallback
        "meta-llama/llama-3.2-3b-instruct",

        # Large fallback
        "nvidia/nemotron-3-ultra-550b-a55b",
    ]

    DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful AI assistant."
    )

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Orion AI System",
            },
        )

        # Model -> unix timestamp until which the model
        # should temporarily be avoided.
        self._cooldowns: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Cooldown handling
    # ------------------------------------------------------------------

    def _is_on_cooldown(self, model: str) -> bool:
        until = self._cooldowns.get(model)

        if until is None:
            return False

        if time.time() >= until:
            self._cooldowns.pop(model, None)
            return False

        return True

    def _cooldown(
        self,
        model: str,
        seconds: int,
    ) -> None:
        self._cooldowns[model] = time.time() + seconds

        print(
            f"Model cooldown: {model} "
            f"for {seconds}s"
        )

    # ------------------------------------------------------------------
    # Retry-After extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _get_retry_after(
        exc: Exception,
        default: int = 30,
    ) -> int:

        try:
            response = getattr(exc, "response", None)

            if response is not None:
                headers = getattr(
                    response,
                    "headers",
                    None,
                )

                if headers:
                    value = headers.get(
                        "Retry-After"
                    )

                    if value:
                        return max(
                            1,
                            int(value),
                        )

        except Exception:
            pass

        return default

    # ------------------------------------------------------------------
    # OpenRouter error classification
    # ------------------------------------------------------------------

    @staticmethod
    def _is_in_flight_budget_error(
        exc: Exception,
    ) -> bool:

        text = str(exc).lower()

        return (
            "in_flight_budget_exhausted" in text
            or "in-flight budget" in text
            or "in flight requests" in text
        )

    @staticmethod
    def _is_prompt_budget_error(
        exc: Exception,
    ) -> bool:

        text = str(exc).lower()

        return (
            "prompt tokens limit exceeded" in text
            or "prompt size" in text
        )

    @staticmethod
    def _status_code(
        exc: Exception,
    ) -> Optional[int]:

        return getattr(exc, "status_code", None)

    # ------------------------------------------------------------------
    # Single model request
    # ------------------------------------------------------------------

    def _request(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
    ) -> str:

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
            max_tokens=500,
        )

        if response is None:
            raise RuntimeError(
                f"{model} returned None response."
            )

        if not response.choices:
            raise RuntimeError(
                f"{model} returned no choices."
            )

        message = response.choices[0].message

        if message is None:
            raise RuntimeError(
                f"{model} returned empty message."
            )

        content = message.content

        if not content or not content.strip():
            raise RuntimeError(
                f"{model} returned empty content."
            )

        return content.strip()

    # ------------------------------------------------------------------
    # Generate
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> str:

        last_error: Optional[Exception] = None

        for model in self.MODELS:

            # ----------------------------------------------------------
            # Skip temporarily unavailable models
            # ----------------------------------------------------------

            if self._is_on_cooldown(model):
                print(
                    f"Skipping {model}: "
                    f"currently on cooldown."
                )
                continue

            try:

                print(
                    f"Trying model: {model}"
                )

                content = self._request(
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                )

                print(
                    f"Model succeeded: {model}"
                )

                return content

            # ----------------------------------------------------------
            # Standard rate limiting
            # ----------------------------------------------------------

            except RateLimitError as exc:

                last_error = exc

                retry_after = self._get_retry_after(
                    exc,
                    default=30,
                )

                print(
                    f"{model} is rate limited. "
                    f"Retry-After={retry_after}s"
                )

                self._cooldown(
                    model,
                    retry_after,
                )

                continue

            # ----------------------------------------------------------
            # OpenRouter status errors
            # ----------------------------------------------------------

            except APIStatusError as exc:

                last_error = exc

                status_code = self._status_code(exc)

                # ------------------------------------------------------
                # 402: in-flight budget exhausted
                # ------------------------------------------------------

                if (
                    status_code == 402
                    and self._is_in_flight_budget_error(exc)
                ):
                    retry_after = self._get_retry_after(
                        exc,
                        default=120,
                    )

                    print(
                        "OpenRouter in-flight budget "
                        "exhausted."
                    )

                    print(
                        f"Waiting {retry_after}s "
                        "before retrying."
                    )

                    # IMPORTANT:
                    #
                    # Do NOT burn through every model.
                    #
                    # This is an account-level concurrency
                    # problem, not necessarily a model problem.
                    time.sleep(retry_after)

                    # Retry the same model once after cooldown.
                    try:
                        print(
                            f"Retrying model after "
                            f"budget cooldown: {model}"
                        )

                        content = self._request(
                            model=model,
                            prompt=prompt,
                            system_prompt=system_prompt,
                        )

                        print(
                            f"Model succeeded: {model}"
                        )

                        return content

                    except Exception as retry_exc:

                        last_error = retry_exc

                        print(
                            "Retry after in-flight "
                            "budget cooldown failed:"
                        )

                        print(retry_exc)

                        # Now move to the next model.
                        continue

                # ------------------------------------------------------
                # 402: prompt too large / insufficient credits
                # ------------------------------------------------------

                if (
                    status_code == 402
                    and self._is_prompt_budget_error(exc)
                ):
                    print(
                        f"{model} rejected the request "
                        "because the prompt is too large "
                        "for the available budget."
                    )

                    print(
                        "Trying another model is unlikely "
                        "to solve this."
                    )

                    return (
                        "The AI request could not be processed "
                        "because the input context is too large. "
                        "Please reduce the amount of context "
                        "and try again."
                    )

                # ------------------------------------------------------
                # Other 402 errors
                # ------------------------------------------------------

                if status_code == 402:

                    print(
                        f"{model} returned OpenRouter 402."
                    )

                    continue

                # ------------------------------------------------------
                # Other HTTP errors
                # ------------------------------------------------------

                print(
                    f"{model} failed with "
                    f"HTTP {status_code}: {exc}"
                )

                traceback.print_exc()

                continue

            # ----------------------------------------------------------
            # Everything else
            # ----------------------------------------------------------

            except Exception as exc:

                last_error = exc

                print(
                    f"{model} failed: {exc}"
                )

                traceback.print_exc()

                continue

        # ----------------------------------------------------------------
        # All models exhausted
        # ----------------------------------------------------------------

        print(
            "All configured LLM models failed."
        )

        if last_error:
            print(
                f"Last LLM error: {last_error}"
            )

        return (
            "Sorry, all available AI models are "
            "currently unavailable. Please try again "
            "in a minute."
        )


llm_service = LLMService()


def generate_response(
    prompt: str,
) -> str:
    return llm_service.generate(prompt)