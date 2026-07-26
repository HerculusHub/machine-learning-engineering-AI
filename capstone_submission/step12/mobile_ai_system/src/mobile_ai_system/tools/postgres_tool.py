"""
PostgreSQL Tool.

Provides access to structured relational data.
"""

from __future__ import annotations

from mobile_ai_system.tools.base import BaseTool


class PostgreSQLTool(BaseTool):
    """
    Tool wrapper for PostgreSQL.

    The actual database implementation will be added in
    a later release.
    """

    NAME = "postgres"

    def __init__(self) -> None:

        self._connected = False

    @property
    def name(self) -> str:

        return self.NAME

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    def connect(self) -> None:
        """
        Placeholder.

        PostgreSQL connection will be added later.
        """

        self._connected = True

    def health_check(self) -> bool:

        return self._connected

    # ---------------------------------------------------------
    # Execute
    # ---------------------------------------------------------

    def execute(
        self,
        sql: str,
        parameters=None,
    ):
        """
        Execute SQL.

        Placeholder implementation.
        """

        raise NotImplementedError(
            "PostgreSQL integration is not implemented yet."
        )