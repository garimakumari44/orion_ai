from __future__ import annotations

from typing import Any, Dict

from app.tools.base.base_tool import BaseTool

from app.tools.company.company_profile_tool import (
    CompanyProfileTool,
)

from app.tools.company.sec_company_tool import (
    SECCompanyTool,
)

from app.tools.company.company_news_tool import (
    CompanyNewsTool,
)

from app.tools.company.market_data_tool import (
    MarketDataTool,
)


class ToolRouter:
    """
    Central gateway for agent tool execution.

    Responsibilities:
    - Register tools
    - Discover tools
    - Execute tools
    """


    def __init__(self):

        self._tools: Dict[str, BaseTool] = {}

        self._register_tools()



    def _register_tools(self) -> None:
        """
        Register system tools.
        """

        tools = [

            CompanyProfileTool(),

            SECCompanyTool(),

            CompanyNewsTool(),

            MarketDataTool(),

        ]


        for tool in tools:

            self.register(tool)



    def register(
        self,
        tool: BaseTool,
    ) -> None:
        """
        Add tool to registry.
        """

        self._tools[tool.name] = tool



    def unregister(
        self,
        tool_name: str,
    ) -> None:
        """
        Remove tool.
        """

        self._tools.pop(
            tool_name,
            None,
        )



    def has_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Check availability.
        """

        return tool_name in self._tools



    def get_tool(
        self,
        tool_name: str,
    ) -> BaseTool | None:
        """
        Retrieve tool instance.
        """

        return self._tools.get(
            tool_name
        )



    async def execute(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute tool.
        """

        tool = self.get_tool(
            tool_name
        )


        if tool is None:

            return {
                "success": False,
                "output": None,
                "error": (
                    f"Unknown tool '{tool_name}'"
                ),
            }


        try:

            return await tool.execute(
                **kwargs
            )


        except Exception as exc:

            return {
                "success": False,
                "output": None,
                "error": str(exc),
            }



    def available_tools(self) -> list[str]:
        """
        List registered tools.
        """

        return sorted(
            self._tools.keys()
        )