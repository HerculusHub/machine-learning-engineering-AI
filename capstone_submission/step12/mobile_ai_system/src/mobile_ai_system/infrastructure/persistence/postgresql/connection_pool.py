"""
PostgreSQL Connection Pool

Architecture v2.0 (Frozen)

Responsibilities
----------------
- Create one shared PostgreSQL connection pool
- Return the shared pool
- Close the shared pool

Does NOT
---------
- Execute SQL
- Manage transactions
- Know about repositories
- Know about memory
"""

from __future__ import annotations

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from mobile_ai_system.core.config import get_settings
from mobile_ai_system.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

# Singleton pool instance
_POOL: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    """
    Return the shared PostgreSQL connection pool.

    Safe to call multiple times.
    """

    global _POOL

    if _POOL is not None:

        return _POOL

    settings = get_settings()

    
    conninfo = (
        f"host={settings.postgres_host} "
        f"port={settings.postgres_port} "
        f"dbname={settings.postgres_database} "
        f"user={settings.postgres_user} "
        f"password={settings.postgres_password} "
        f"connect_timeout={settings.postgres_connect_timeout}"
    )

    logger.info("Creating PostgreSQL connection pool...")

    _POOL = ConnectionPool(
        conninfo=conninfo,

        # Initial connections
        min_size=1,

        # Maximum simultaneous connections
        max_size=settings.postgres_pool_size,

        # Wait at most this many seconds
        timeout=30,

        kwargs={
            "row_factory": dict_row,
        },

        open=True,
    )

    logger.info("PostgreSQL connection pool created.")

    return _POOL


def health_check() -> bool:
    """
    Verify the pool can connect to PostgreSQL.
    """

    try:

        pool = get_pool()

        with pool.connection() as conn:

            with conn.cursor() as cursor:

                cursor.execute("SELECT 1;")

                cursor.fetchone()

        logger.info("PostgreSQL pool health check passed.")

        return True

    except Exception as exc:

        logger.exception(
            "PostgreSQL pool health check failed: %s",
            exc,
        )

        return False


def close_pool() -> None:
    """
    Close the shared PostgreSQL connection pool.

    Safe to call multiple times.
    """

    global _POOL

    if _POOL is None:

        return

    logger.info("Closing PostgreSQL connection pool...")

    _POOL.close()

    _POOL = None

    logger.info("PostgreSQL connection pool closed.")