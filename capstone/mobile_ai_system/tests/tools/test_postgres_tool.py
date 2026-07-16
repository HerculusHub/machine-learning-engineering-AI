from mobile_ai_system.tools.postgres_tool import PostgreSQLTool


def test_name():

    tool = PostgreSQLTool()

    assert tool.name == "postgres"


def test_connect():

    tool = PostgreSQLTool()

    tool.connect()

    assert tool.health_check()