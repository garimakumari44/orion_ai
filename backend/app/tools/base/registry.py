"""
Tool Registry

Central storage for all available tools.

Example:

SEC Filing Tool
Market Data Tool
News Tool
Macro Tool

are registered here.

Tool Router uses this registry
to discover and execute tools.
"""

from typing import Dict, List

from .base_tool import BaseTool



class ToolRegistry:

    """
    Global tool registry.
    """


    def __init__(self):

        self._tools: Dict[str, BaseTool] = {}



    # --------------------------------
    # Register Tool
    # --------------------------------

    def register(
        self,
        tool: BaseTool
    ):
        """
        Add a tool to registry.
        """

        name = tool.name


        if name in self._tools:

            raise ValueError(
                f"Tool already registered: {name}"
            )


        self._tools[name] = tool



    # --------------------------------
    # Remove Tool
    # --------------------------------

    def unregister(
        self,
        name: str
    ):

        if name in self._tools:

            del self._tools[name]



    # --------------------------------
    # Get Tool
    # --------------------------------

    def get(
        self,
        name: str
    ) -> BaseTool:
        """
        Retrieve a tool.
        """

        tool = self._tools.get(name)


        if not tool:

            raise KeyError(
                f"Tool not found: {name}"
            )


        return tool



    # --------------------------------
    # List Tools
    # --------------------------------

    def list_tools(self) -> List[dict]:
        """
        Return tool metadata.
        """

        return [

            tool.metadata()

            for tool in self._tools.values()

        ]



    # --------------------------------
    # Check Tool Exists
    # --------------------------------

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self._tools



    # --------------------------------
    # Count
    # --------------------------------

    def count(self):

        return len(self._tools)



# Global registry instance

tool_registry = ToolRegistry()