from mobile_ai_system.tools.vector_tool import VectorTool


def test_vector():

    tool = VectorTool()

    tool.connect()

    assert tool.health_check()