from mobile_ai_system.tools.tool_registry import ToolRegistry


def test_registry():

    registry = ToolRegistry()

    assert "mongo" in registry.list_tools()

    assert "llm" in registry.list_tools()

    assert registry.get("mongo").name == "MongoTool"