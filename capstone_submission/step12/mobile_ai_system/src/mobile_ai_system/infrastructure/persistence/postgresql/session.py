"""
Database Session

Architecture v2.0 (Frozen)

Responsibilities
----------------
- Acquire a pooled connection
- Create cursors
- Commit successful transactions
- Roll back failed transactions

Owns transaction boundaries only.
"""

from __future__ import annotations

from contextlib import contextmanager

from psycopg import Connection

from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.infrastructure.persistence.postgresql.connection_pool import (
    get_pool,
)

logger = get_logger(__name__)


class DatabaseSession:
    """
    Transaction manager.

    Example
    -------
    with DatabaseSession() as session:

        with session.cursor() as cursor:
            cursor.execute("SELECT 1")
    """

    def __init__(self):
        self._conn_context = None
        self._connection: Connection | None = None

    # ---------------------------------------------------------
    # Context Manager (Transaction Boundary)
    # ---------------------------------------------------------

    def __enter__(self):
        self._conn_context = get_pool().connection()
        self._connection = self._conn_context.__enter__()

        logger.debug("Database session started.")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._connection is None:
            return False

        try:
            if exc_type is None:
                self._connection.commit()
                logger.debug("Transaction committed.")
            else:
                self._connection.rollback()
                logger.exception("Transaction rolled back.")

        finally:
            self._conn_context.__exit__(exc_type, exc_value, traceback)

            logger.debug("Connection returned to pool.")

            self._connection = None
            self._conn_context = None

        return False

    # ---------------------------------------------------------
    # Cursor (NOW FIXED: context manager)
    # ---------------------------------------------------------
    
    def cursor(self):
        """
        Return raw DB cursor (NO context manager).
        """
        if self._connection is None:
            raise RuntimeError("DatabaseSession is not active.")

        return self._connection.cursor()


    