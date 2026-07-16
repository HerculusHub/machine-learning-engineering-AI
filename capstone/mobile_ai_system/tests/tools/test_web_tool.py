from mobile_ai_system.tools.web_tool import WebTool


def test_web():

    tool = WebTool()

    assert tool.health_check()