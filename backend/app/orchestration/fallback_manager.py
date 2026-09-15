from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.tools.base_tool import BaseTool

from .capability import Capability
from .tool_registry import ToolRegistry


logger = logging.getLogger(__name__)


class FallbackManager:
    """
    Determines which tool should be tried after a failure.

    Example:

        primary_tool
              |
              v
        fallback_tool
              |
              v
        another_tool

    Responsibilities:
    - Store fallback chains
    - Select next available fallback tool
    - Prevent fallback loops
    - Validate capability compatibility
    """

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:

        self.registry = registry

        # Example:
        #
        # {
        #    "primary": ["fallback", "backup"]
        # }
        #
        self._fallbacks: Dict[str, List[str]] = {}


    # =========================================================
    # Registration
    # =========================================================

    def register(
        self,
        tool_name: str,
        fallback_tools: List[str],
    ) -> None:
        """
        Register fallback chain.

        Example:

            primary -> fallback
        """

        self._fallbacks[tool_name] = fallback_tools

        logger.info(
            "Registered fallback chain: %s -> %s",
            tool_name,
            fallback_tools,
        )


    # =========================================================
    # Lookup
    # =========================================================

    def get_next_tool(
        self,
        failed_tool: str,
        attempted_tools: List[str],
        capability: Capability,
    ) -> Optional[BaseTool]:
        """
        Find the next usable fallback tool.

        Conditions:
        - Must be registered as fallback
        - Must not already be attempted
        - Must exist in registry
        - Must support capability
        - Must be available

        Returns:
            BaseTool | None
        """

        candidates = self._fallbacks.get(
            failed_tool,
            [],
        )


        logger.info(
            "Searching fallback for '%s'. Candidates=%s",
            failed_tool,
            candidates,
        )


        for candidate_name in candidates:


            # Prevent infinite loops
            if candidate_name in attempted_tools:

                logger.warning(
                    "Skipping already attempted fallback '%s'",
                    candidate_name,
                )

                continue


            # Find tool
            tool = self.registry.get(
                candidate_name
            )


            if tool is None:

                logger.warning(
                    "Fallback tool '%s' not found",
                    candidate_name,
                )

                continue



            # Capability check
            if not tool.supports(capability):

                logger.warning(
                    "Fallback '%s' does not support capability %s",
                    candidate_name,
                    capability,
                )

                continue



            # Availability check
            if not tool.is_available():

                logger.warning(
                    "Fallback '%s' is unavailable",
                    candidate_name,
                )

                continue



            logger.info(
                "Selected fallback tool '%s'",
                candidate_name,
            )


            return tool



        logger.error(
            "No usable fallback found for '%s'",
            failed_tool,
        )

        return None



    # =========================================================
    # Utility
    # =========================================================

    def has_fallback(
        self,
        tool_name: str,
    ) -> bool:
        """
        Check whether a tool has fallback options.
        """

        return tool_name in self._fallbacks



    def clear(self) -> None:
        """
        Remove all fallback rules.
        """

        self._fallbacks.clear()



    def all(self) -> Dict[str, List[str]]:
        """
        Return registered fallback chains.
        """

        return dict(self._fallbacks)