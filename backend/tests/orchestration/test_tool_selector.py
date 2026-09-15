import pytest

from app.orchestration.tool_selector import (
    ToolSelector,
    ToolSelectionError
)

from app.orchestration.capability import Capability



def test_select_best_priority(
    tool_registry
):

    from tests.orchestration.conftest import FakeTool


    tool1 = FakeTool(
        name="low",
        priority=1
    )

    tool2 = FakeTool(
        name="high",
        priority=10
    )


    tool_registry.register(tool1)
    tool_registry.register(tool2)



    selector = ToolSelector(
        tool_registry
    )


    selected = selector.select(
        Capability.WEB_SEARCH
    )


    assert selected.name=="high"




def test_selector_ignores_disabled_tools(
    tool_registry
):

    from tests.orchestration.conftest import FakeTool


    tool = FakeTool(
        enabled=False
    )


    tool_registry.register(tool)


    selector = ToolSelector(
        tool_registry
    )


    with pytest.raises(
        ToolSelectionError
    ):

        selector.select(
            Capability.WEB_SEARCH
        )



def test_selector_ignores_unhealthy_tools(
    tool_registry
):

    from tests.orchestration.conftest import FakeTool


    tool = FakeTool(
        healthy=False
    )


    tool_registry.register(tool)


    selector = ToolSelector(
        tool_registry
    )


    with pytest.raises(
        ToolSelectionError
    ):

        selector.select(
            Capability.WEB_SEARCH
        )



def test_no_capability():

    from app.orchestration.tool_registry import ToolRegistry


    registry = ToolRegistry()


    selector = ToolSelector(
        registry
    )


    with pytest.raises(
        ToolSelectionError
    ):

        selector.select(
            Capability.WEB_SEARCH
        )