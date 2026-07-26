from mobile_ai_system.tools.mongo_tool import MongoTool


def test_tool_name():

    tool = MongoTool()

    assert tool.name == "MongoTool"


def test_health():

    tool = MongoTool()

    assert tool.health_check() is True

    tool.close()


def test_search():

    tool = MongoTool()

    results = tool.search("Verizon")

    assert isinstance(results, list)

    tool.close()