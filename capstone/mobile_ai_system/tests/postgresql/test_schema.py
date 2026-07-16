from mobile_ai_system.infrastructure.persistence.postgresql.schema import (
    SchemaManager,
)
from mobile_ai_system.infrastructure.persistence.postgresql.client import (
    PostgreSQLClient,
)
from mobile_ai_system.infrastructure.persistence.postgresql.session import (
    DatabaseSession,
)


def test_schema_creation():

    SchemaManager().initialize()

    with DatabaseSession() as session:

        client = PostgreSQLClient(session)

        tables = client.fetch_all(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname='public';
            """
        )

    names = {row["tablename"] for row in tables}

    assert "episodes" in names
    assert "reflections" in names
    assert "semantic_memory" in names
    assert "execution_history" in names