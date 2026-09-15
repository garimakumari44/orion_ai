import pytest

from app.orchestration.capability import Capability


def test_register_tool(
    tool_registry,
    fake_tool
):

    tool_registry.register(fake_tool)


    assert tool_registry.has_tool(
        "fake_tool"
    )


    assert len(tool_registry) == 1



def test_get_tool(
    tool_registry,
    fake_tool
):

    tool_registry.register(fake_tool)

    result = tool_registry.get(
        "fake_tool"
    )


    assert result == fake_tool



def test_duplicate_registration(
    tool_registry,
    fake_tool
):

    tool_registry.register(fake_tool)


    with pytest.raises(ValueError):

        tool_registry.register(fake_tool)



def test_find_by_capability(
    tool_registry,
    fake_tool
):

    tool_registry.register(fake_tool)


    tools = tool_registry.find_by_capability(
        Capability.WEB_SEARCH
    )


    assert len(tools)==1

    assert tools[0].name=="fake_tool"



def test_unregister(
    tool_registry,
    fake_tool
):

    tool_registry.register(fake_tool)

    tool_registry.unregister(
        "fake_tool"
    )


    assert not tool_registry.has_tool(
        "fake_tool"
    )



def test_clear_registry(
    tool_registry,
    fake_tool
):

    tool_registry.register(fake_tool)


    tool_registry.clear()


    assert len(tool_registry)==0