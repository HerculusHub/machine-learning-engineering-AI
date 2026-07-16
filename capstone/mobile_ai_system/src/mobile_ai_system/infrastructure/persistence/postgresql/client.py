"""
PostgreSQL Client

Architecture v2.0 (Frozen)

Responsibilities
----------------
- Execute SQL statements
- Fetch one row
- Fetch many rows
- Execute INSERT/UPDATE/DELETE
- Bulk execution

The client NEVER opens or closes connections.
The client NEVER commits or rolls back transactions.
Those responsibilities belong to DatabaseSession.
"""

from __future__ import annotations

from typing import Any


from psycopg.types.json import Jsonb

from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.infrastructure.persistence.postgresql.session import (
    DatabaseSession,
)

logger = get_logger(__name__)


class PostgreSQLClient:
    """
    Thin SQL execution wrapper.

    A DatabaseSession manages the connection and transaction.
    """

    def __init__(self, session: DatabaseSession):

        self._session = session

    
    # ---------------------------------------------------------
    # Parameter Conversion
    # ---------------------------------------------------------

    def _adapt_params(
        self,
        params: tuple[Any, ...] | None,
    ) -> tuple[Any, ...] | None:
        """
        Convert Python objects into PostgreSQL-compatible types.

        Automatically wraps dictionaries and lists as JSONB.
        """

        if params is None:

            return None

        adapted = []

        for value in params:

            if isinstance(value, (dict, list)):

                adapted.append(Jsonb(value))

            else:

                adapted.append(value)

        return tuple(adapted)

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def fetch_one(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
    ) -> dict[str, Any] | None:
        """
        Execute a SELECT query and return one row.
        """

        cursor = self._session.cursor()

        cursor.execute(
            sql,
            self._adapt_params(params),
        )

        return cursor.fetchone()

    def fetch_all(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a SELECT query and return all rows.
        """

        cursor = self._session.cursor()

        cursor.execute(
            sql,
            self._adapt_params(params),
        )
        
        return cursor.fetchall()

    # ---------------------------------------------------------
    # Write
    # ---------------------------------------------------------

    def execute_non_query(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
    ) -> None:
        """
        Execute INSERT, UPDATE, DELETE, or DDL.
        """

        cursor = self._session.cursor()

        cursor.execute(
            sql,
            self._adapt_params(params),
        )

    # ---------------------------------------------------------
    # Bulk Write
    # ---------------------------------------------------------

    def execute_many(
        self,
        sql: str,
        values: list[tuple],
    ) -> None:
        """
        Execute many SQL statements efficiently.
        """

        cursor = self._session.cursor()

        adapted_values = [
            self._adapt_params(value)

            for value in values
        ]

        cursor.executemany(
            sql,
            adapted_values,
        )

    # ---------------------------------------------------------
    # Health Check
    # ---------------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify that the database connection is alive.
        """

        try:

            result = self.fetch_one(
                "SELECT 1 AS ok;"
            )

            return result is not None and result["ok"] == 1

        except Exception as exc:

            logger.exception(
                "PostgreSQL health check failed: %s",
                exc,
            )

            return False