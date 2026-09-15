"""
app/llm/context/budget.py

Centralized LLM Context Budget Manager.

This is the single application-level authority responsible for preparing
input context before provider routing/execution.

Architecture:

    Agent / Planner / Tool / Knowledge System
                    |
                    v
                LLMManager
                    |
                    v
              ContextBudget
                    |
                    v
             ModelRouter
                    |
                    v
            ProviderRouter
                    |
                    v
              LLM Provider
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import math
from typing import Any, Optional

from app.llm.constants import (
    DEFAULT_CHARS_PER_TOKEN,
    DEFAULT_CONTEXT_BUDGET,
    MIN_INPUT_TOKENS,
    MIN_MESSAGE_TOKENS,
    TRUNCATION_MARKER,
)


logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================


class ContextBudgetError(RuntimeError):
    """Base context-budget exception."""


class PromptTooLargeError(ContextBudgetError):
    """Raised when the request cannot fit the configured budget."""


# ============================================================================
# RESULT
# ============================================================================


@dataclass(slots=True, frozen=True)
class ContextBudgetResult:
    content: str
    messages: list[dict[str, Any]]

    original_tokens: int
    prepared_tokens: int

    budget: int
    reserved_output_tokens: int

    truncated: bool

    messages_removed: int
    characters_removed: int

    reason: str


# ============================================================================
# CONTEXT BUDGET
# ============================================================================


class ContextBudget:
    """
    Centralized deterministic context preparation.

    Important invariants:

    1. A valid input request must never produce an empty message list.
    2. Context reduction should prefer truncation over deleting the
       final remaining message.
    3. If a request genuinely cannot fit, PromptTooLargeError is raised.
    4. The class remains provider-independent.
    """

    def __init__(
        self,
        max_context_tokens: int = DEFAULT_CONTEXT_BUDGET,
        *,
        chars_per_token: int = DEFAULT_CHARS_PER_TOKEN,
        min_input_tokens: int = MIN_INPUT_TOKENS,
    ) -> None:

        self._validate_positive_int(
            max_context_tokens,
            "max_context_tokens",
        )

        self._validate_positive_int(
            chars_per_token,
            "chars_per_token",
        )

        self._validate_positive_int(
            min_input_tokens,
            "min_input_tokens",
        )

        if min_input_tokens >= max_context_tokens:
            raise ValueError(
                "min_input_tokens must be smaller than "
                "max_context_tokens."
            )

        self._max_context_tokens = max_context_tokens
        self._chars_per_token = chars_per_token
        self._min_input_tokens = min_input_tokens

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def max_context_tokens(self) -> int:
        return self._max_context_tokens

    @property
    def chars_per_token(self) -> int:
        return self._chars_per_token

    @property
    def min_input_tokens(self) -> int:
        return self._min_input_tokens

    # ========================================================================
    # TOKEN ESTIMATION
    # ========================================================================

    def estimate_tokens(
        self,
        text: Optional[str],
    ) -> int:

        if text is None:
            return 0

        if not isinstance(text, str):
            text = str(text)

        if not text:
            return 0

        return max(
            1,
            math.ceil(
                len(text) / self._chars_per_token
            ),
        )

    def estimate_message_tokens(
        self,
        message: dict[str, Any],
    ) -> int:

        if not isinstance(message, dict):
            return 0

        content = message.get(
            "content"
        )

        if isinstance(content, str):

            content_tokens = (
                self.estimate_tokens(
                    content
                )
            )

        elif isinstance(content, list):

            content_tokens = (
                self._estimate_structured_content(
                    content
                )
            )

        elif content is None:

            content_tokens = 0

        else:

            content_tokens = (
                self.estimate_tokens(
                    str(content)
                )
            )

        return content_tokens + 4

    def estimate_messages_tokens(
        self,
        messages: list[dict[str, Any]],
    ) -> int:

        if not isinstance(messages, list):
            raise TypeError(
                "messages must be a list."
            )

        return sum(
            self.estimate_message_tokens(
                message
            )
            for message in messages
        )

    # ========================================================================
    # PROMPT
    # ========================================================================

    def prepare_prompt(
        self,
        prompt: str,
        *,
        reserved_output_tokens: int = 0,
    ) -> ContextBudgetResult:

        self._validate_prompt(
            prompt
        )

        budget = self._calculate_input_budget(
            reserved_output_tokens
        )

        original_tokens = (
            self.estimate_tokens(
                prompt
            )
        )

        if original_tokens <= budget:

            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]

            return ContextBudgetResult(
                content=prompt,
                messages=messages,
                original_tokens=original_tokens,
                prepared_tokens=original_tokens,
                budget=budget,
                reserved_output_tokens=reserved_output_tokens,
                truncated=False,
                messages_removed=0,
                characters_removed=0,
                reason=(
                    "Prompt already fits context budget."
                ),
            )

        prepared = (
            self._truncate_text_to_tokens(
                prompt,
                budget,
            )
        )

        prepared_tokens = (
            self.estimate_tokens(
                prepared
            )
        )

        if prepared_tokens > budget:
            raise PromptTooLargeError(
                "Prompt cannot fit inside the configured "
                f"input budget of {budget} tokens."
            )

        messages = [
            {
                "role": "user",
                "content": prepared,
            }
        ]

        # Safety invariant.
        self._validate_messages(
            messages
        )

        return ContextBudgetResult(
            content=prepared,
            messages=messages,
            original_tokens=original_tokens,
            prepared_tokens=prepared_tokens,
            budget=budget,
            reserved_output_tokens=reserved_output_tokens,
            truncated=True,
            messages_removed=0,
            characters_removed=max(
                0,
                len(prompt) - len(prepared),
            ),
            reason=(
                "Prompt exceeded the input budget and was "
                "deterministically truncated."
            ),
        )

    # ========================================================================
    # MESSAGES
    # ========================================================================

    def prepare_messages(
        self,
        messages: list[dict[str, Any]],
        *,
        reserved_output_tokens: int = 0,
    ) -> list[dict[str, Any]]:

        return self.prepare_messages_with_result(
            messages,
            reserved_output_tokens=reserved_output_tokens,
        ).messages

    def prepare_messages_with_result(
        self,
        messages: list[dict[str, Any]],
        *,
        reserved_output_tokens: int = 0,
    ) -> ContextBudgetResult:

        self._validate_messages(
            messages
        )

        budget = self._calculate_input_budget(
            reserved_output_tokens
        )

        original_tokens = (
            self.estimate_messages_tokens(
                messages
            )
        )

        copied = self._copy_messages(
            messages
        )

        if original_tokens <= budget:

            self._validate_messages(
                copied
            )

            return ContextBudgetResult(
                content=self._messages_to_text(
                    copied
                ),
                messages=copied,
                original_tokens=original_tokens,
                prepared_tokens=original_tokens,
                budget=budget,
                reserved_output_tokens=reserved_output_tokens,
                truncated=False,
                messages_removed=0,
                characters_removed=0,
                reason=(
                    "Messages already fit context budget."
                ),
            )

        (
            prepared,
            removed_count,
            removed_chars,
        ) = self._fit_messages(
            copied,
            budget,
        )

        # ------------------------------------------------------------
        # HARD SAFETY INVARIANT
        # ------------------------------------------------------------

        if not prepared:

            raise PromptTooLargeError(
                "ContextBudget produced an empty message list. "
                "At least one message must remain."
            )

        self._validate_messages(
            prepared
        )

        prepared_tokens = (
            self.estimate_messages_tokens(
                prepared
            )
        )

        if prepared_tokens > budget:

            raise PromptTooLargeError(
                "Messages cannot fit inside the configured "
                f"input budget of {budget} tokens."
            )

        return ContextBudgetResult(
            content=self._messages_to_text(
                prepared
            ),
            messages=prepared,
            original_tokens=original_tokens,
            prepared_tokens=prepared_tokens,
            budget=budget,
            reserved_output_tokens=reserved_output_tokens,
            truncated=True,
            messages_removed=removed_count,
            characters_removed=removed_chars,
            reason=(
                "Older context was removed and/or oversized "
                "content was deterministically truncated."
            ),
        )

    # ========================================================================
    # BUDGET
    # ========================================================================

    def _calculate_input_budget(
        self,
        reserved_output_tokens: int,
    ) -> int:

        self._validate_nonnegative_int(
            reserved_output_tokens,
            "reserved_output_tokens",
        )

        if reserved_output_tokens >= self._max_context_tokens:

            raise PromptTooLargeError(
                "Reserved output tokens "
                f"({reserved_output_tokens}) consume the entire "
                f"context budget ({self._max_context_tokens})."
            )

        budget = (
            self._max_context_tokens
            - reserved_output_tokens
        )

        if budget < self._min_input_tokens:

            raise PromptTooLargeError(
                "Insufficient input context remains after "
                f"reserving {reserved_output_tokens} output tokens."
            )

        return budget

    # ========================================================================
    # MESSAGE FITTING
    # ========================================================================

    def _fit_messages(
        self,
        messages: list[dict[str, Any]],
        budget: int,
    ) -> tuple[
        list[dict[str, Any]],
        int,
        int,
    ]:

        working = self._copy_messages(
            messages
        )

        removed_count = 0
        removed_chars = 0

        # --------------------------------------------------------------------
        # PHASE 1
        #
        # Remove oldest non-system messages.
        #
        # IMPORTANT:
        # Never remove the final remaining message.
        # --------------------------------------------------------------------

        while (
            self.estimate_messages_tokens(
                working
            )
            > budget
        ):

            index = (
                self._oldest_removable_index(
                    working
                )
            )

            if index is None:
                break

            # Never allow:
            #
            # [message] -> []
            #
            if len(working) <= 1:
                break

            removed = working.pop(
                index
            )

            removed_count += 1

            removed_chars += (
                self._message_char_count(
                    removed
                )
            )

        # --------------------------------------------------------------------
        # PHASE 2
        #
        # Truncate the largest message.
        # --------------------------------------------------------------------

        while (
            self.estimate_messages_tokens(
                working
            )
            > budget
        ):

            index = (
                self._largest_truncatable_index(
                    working
                )
            )

            if index is None:
                break

            current = working[index]

            current_tokens = (
                self.estimate_message_tokens(
                    current
                )
            )

            total_tokens = (
                self.estimate_messages_tokens(
                    working
                )
            )

            excess = (
                total_tokens - budget
            )

            target_tokens = max(
                MIN_MESSAGE_TOKENS,
                current_tokens - excess - 4,
            )

            truncated = (
                self._truncate_message(
                    current,
                    target_tokens,
                )
            )

            new_tokens = (
                self.estimate_message_tokens(
                    truncated
                )
            )

            # ------------------------------------------------------------
            # Truncation made no progress.
            # ------------------------------------------------------------

            if new_tokens >= current_tokens:

                role = str(
                    current.get(
                        "role",
                        "",
                    )
                ).strip().lower()

                # Never remove the final message.
                if len(working) <= 1:
                    break

                if role != "system":

                    removed = working.pop(
                        index
                    )

                    removed_count += 1

                    removed_chars += (
                        self._message_char_count(
                            removed
                        )
                    )

                    continue

                # --------------------------------------------------------
                # Last-resort system-message truncation.
                # --------------------------------------------------------

                if current_tokens > MIN_MESSAGE_TOKENS:

                    target_tokens = max(
                        8,
                        current_tokens - excess - 4,
                    )

                    truncated = (
                        self._truncate_message(
                            current,
                            target_tokens,
                        )
                    )

                    new_tokens = (
                        self.estimate_message_tokens(
                            truncated
                        )
                    )

                    if new_tokens < current_tokens:

                        removed_chars += max(
                            0,
                            self._message_char_count(
                                current
                            )
                            - self._message_char_count(
                                truncated
                            ),
                        )

                        working[index] = truncated

                        continue

                break

            # ------------------------------------------------------------
            # Successful truncation.
            # ------------------------------------------------------------

            removed_chars += max(
                0,
                self._message_char_count(
                    current
                )
                - self._message_char_count(
                    truncated
                ),
            )

            working[index] = truncated

        # --------------------------------------------------------------------
        # PHASE 3
        #
        # Remove additional non-system messages if necessary.
        #
        # NEVER remove the final remaining message.
        # --------------------------------------------------------------------

        while (
            self.estimate_messages_tokens(
                working
            )
            > budget
        ):

            index = (
                self._oldest_removable_index(
                    working
                )
            )

            if index is None:
                break

            if len(working) <= 1:
                break

            removed = working.pop(
                index
            )

            removed_count += 1

            removed_chars += (
                self._message_char_count(
                    removed
                )
            )

        # --------------------------------------------------------------------
        # FINAL SAFETY INVARIANT
        # --------------------------------------------------------------------

        if not working:

            raise PromptTooLargeError(
                "ContextBudget removed all messages. "
                "At least one message must remain."
            )

        return (
            working,
            removed_count,
            removed_chars,
        )

    def _oldest_removable_index(
        self,
        messages: list[dict[str, Any]],
    ) -> Optional[int]:

        for index, message in enumerate(
            messages
        ):

            role = str(
                message.get(
                    "role",
                    "",
                )
            ).strip().lower()

            if role != "system":
                return index

        return None

    def _largest_truncatable_index(
        self,
        messages: list[dict[str, Any]],
    ) -> Optional[int]:

        candidates: list[
            tuple[int, int]
        ] = []

        for index, message in enumerate(
            messages
        ):

            role = str(
                message.get(
                    "role",
                    "",
                )
            ).strip().lower()

            if role == "system":
                continue

            tokens = (
                self.estimate_message_tokens(
                    message
                )
            )

            if tokens > MIN_MESSAGE_TOKENS:

                candidates.append(
                    (
                        index,
                        tokens,
                    )
                )

        if candidates:

            return max(
                candidates,
                key=lambda item: item[1],
            )[0]

        # Last resort: system message.
        for index, message in enumerate(
            messages
        ):

            if (
                self.estimate_message_tokens(
                    message
                )
                > MIN_MESSAGE_TOKENS
            ):

                return index

        return None

    # ========================================================================
    # TEXT TRUNCATION
    # ========================================================================

    def _truncate_text_to_tokens(
        self,
        text: str,
        target_tokens: int,
    ) -> str:

        if not text:
            return text

        if target_tokens <= 0:

            raise PromptTooLargeError(
                "No input tokens are available."
            )

        current_tokens = (
            self.estimate_tokens(
                text
            )
        )

        if current_tokens <= target_tokens:
            return text

        marker_tokens = (
            self.estimate_tokens(
                TRUNCATION_MARKER
            )
        )

        if target_tokens <= marker_tokens + 2:

            return "[...context truncated...]"

        available_tokens = (
            target_tokens
            - marker_tokens
        )

        available_chars = (
            available_tokens
            * self._chars_per_token
        )

        if available_chars <= 2:

            return "[...context truncated...]"

        head_chars = max(
            1,
            int(
                available_chars * 0.60
            ),
        )

        tail_chars = max(
            1,
            available_chars - head_chars,
        )

        if (
            head_chars + tail_chars
            >= len(text)
        ):

            return text

        return (
            text[:head_chars]
            + TRUNCATION_MARKER
            + text[-tail_chars:]
        )

    # ========================================================================
    # MESSAGE TRUNCATION
    # ========================================================================

    def _truncate_message(
        self,
        message: dict[str, Any],
        target_tokens: int,
    ) -> dict[str, Any]:

        result = dict(
            message
        )

        content = result.get(
            "content"
        )

        if isinstance(content, str):

            result["content"] = (
                self._truncate_text_to_tokens(
                    content,
                    max(
                        1,
                        target_tokens - 4,
                    ),
                )
            )

            return result

        if isinstance(content, list):

            result["content"] = (
                self._truncate_structured_content(
                    content,
                    max(
                        1,
                        target_tokens - 4,
                    ),
                )
            )

            return result

        result["content"] = (
            self._truncate_text_to_tokens(
                str(
                    content or ""
                ),
                max(
                    1,
                    target_tokens - 4,
                ),
            )
        )

        return result

    # ========================================================================
    # STRUCTURED CONTENT
    # ========================================================================

    def _estimate_structured_content(
        self,
        content: list[Any],
    ) -> int:

        total = 0

        for item in content:

            if isinstance(item, str):

                total += (
                    self.estimate_tokens(
                        item
                    )
                )

            elif isinstance(item, dict):

                total += (
                    self.estimate_tokens(
                        str(item)
                    )
                )

            else:

                total += (
                    self.estimate_tokens(
                        str(item)
                    )
                )

        return total + 4

    def _truncate_structured_content(
        self,
        content: list[Any],
        target_tokens: int,
    ) -> list[Any]:

        result: list[Any] = []

        remaining = max(
            1,
            target_tokens,
        )

        for item in content:

            if remaining <= 0:
                break

            if isinstance(item, str):

                allowed = max(
                    1,
                    remaining,
                )

                truncated = (
                    self._truncate_text_to_tokens(
                        item,
                        allowed,
                    )
                )

                result.append(
                    truncated
                )

                remaining -= (
                    self.estimate_tokens(
                        truncated
                    )
                )

                continue

            if isinstance(item, dict):

                copied = dict(
                    item
                )

                text_key: Optional[str] = None

                for key in (
                    "text",
                    "content",
                ):

                    value = copied.get(
                        key
                    )

                    if isinstance(
                        value,
                        str,
                    ):

                        text_key = key
                        break

                if text_key is not None:

                    copied[text_key] = (
                        self._truncate_text_to_tokens(
                            copied[text_key],
                            max(
                                1,
                                remaining,
                            ),
                        )
                    )

                item_tokens = (
                    self.estimate_tokens(
                        str(copied)
                    )
                )

                if item_tokens > remaining:

                    if text_key is None:
                        break

                    copied[text_key] = (
                        self._truncate_text_to_tokens(
                            str(
                                copied[text_key]
                            ),
                            max(
                                1,
                                remaining,
                            ),
                        )
                    )

                    item_tokens = (
                        self.estimate_tokens(
                            str(copied)
                        )
                    )

                if item_tokens > remaining:
                    break

                result.append(
                    copied
                )

                remaining -= item_tokens

                continue

            text = str(item)

            truncated = (
                self._truncate_text_to_tokens(
                    text,
                    max(
                        1,
                        remaining,
                    ),
                )
            )

            result.append(
                truncated
            )

            remaining -= (
                self.estimate_tokens(
                    truncated
                )
            )

        return result

    # ========================================================================
    # VALIDATION
    # ========================================================================

    @staticmethod
    def _validate_positive_int(
        value: int,
        name: str,
    ) -> None:

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
        ):

            raise TypeError(
                f"{name} must be an integer."
            )

        if value <= 0:

            raise ValueError(
                f"{name} must be greater than zero."
            )

    @staticmethod
    def _validate_nonnegative_int(
        value: int,
        name: str,
    ) -> None:

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
        ):

            raise TypeError(
                f"{name} must be an integer."
            )

        if value < 0:

            raise ValueError(
                f"{name} cannot be negative."
            )

    @staticmethod
    def _validate_prompt(
        prompt: str,
    ) -> None:

        if not isinstance(prompt, str):

            raise TypeError(
                "prompt must be a string."
            )

        if not prompt.strip():

            raise ValueError(
                "prompt cannot be empty."
            )

    @staticmethod
    def _validate_messages(
        messages: list[dict[str, Any]],
    ) -> None:

        if not isinstance(messages, list):

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
                    f"messages[{index}] must be a dictionary."
                )

            role = message.get(
                "role"
            )

            if not isinstance(
                role,
                str,
            ):

                raise TypeError(
                    f"messages[{index}].role must be a string."
                )

            if not role.strip():

                raise ValueError(
                    f"messages[{index}].role cannot be empty."
                )

            if "content" not in message:

                raise ValueError(
                    f"messages[{index}] is missing 'content'."
                )

    # ========================================================================
    # HELPERS
    # ========================================================================

    @staticmethod
    def _copy_messages(
        messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        result: list[
            dict[str, Any]
        ] = []

        for message in messages:

            copied = dict(
                message
            )

            content = copied.get(
                "content"
            )

            if isinstance(
                content,
                list,
            ):

                copied["content"] = list(
                    content
                )

            result.append(
                copied
            )

        return result

    @staticmethod
    def _message_char_count(
        message: dict[str, Any],
    ) -> int:

        content = message.get(
            "content"
        )

        if isinstance(
            content,
            str,
        ):

            return len(content)

        if content is None:
            return 0

        return len(
            str(content)
        )

    @staticmethod
    def _messages_to_text(
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

            else:

                parts.append(
                    f"{role}: {content}"
                )

        return "\n".join(
            parts
        )

    # ========================================================================
    # REPRESENTATION
    # ========================================================================

    def __repr__(self) -> str:

        return (
            "ContextBudget("
            f"max_context_tokens="
            f"{self._max_context_tokens}, "
            f"chars_per_token="
            f"{self._chars_per_token}"
            ")"
        )