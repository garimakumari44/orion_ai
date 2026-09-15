import pytest

from app.orchestration.tool_registry import ToolRegistry
from app.tools.base_tool import BaseTool
from app.orchestration.capability import Capability


class FakeTool(BaseTool):

    def __init__(
        self,
        name="fake_tool",
        priority=1,
        enabled=True,
        healthy=True,
        capabilities=None,
        should_fail=False,
    ):

        self.name = name
        self.priority = priority
        self.enabled = enabled
        self.healthy = healthy
        self.capabilities = capabilities or [
               Capability.WEB_SEARCH
]

        self.should_fail = should_fail


    async def execute(self, **kwargs):

        if self.should_fail:
            raise Exception("Tool failed")

        return {
            "message": "success"
        }



@pytest.fixture
def tool_registry():

    return ToolRegistry()



@pytest.fixture
def fake_tool():

    return FakeTool()