from mobile_ai_system.tools.llm_tool import LLMTool


def test_llm():

    tool = LLMTool()

    assert tool.health_check()