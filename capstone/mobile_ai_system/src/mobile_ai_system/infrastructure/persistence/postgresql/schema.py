"""
Schema Manager

Architecture v2.2 (Frozen)

Responsibilities
----------------
- Initialize PostgreSQL schema
- Execute SQL migration files
- Keep database schema up to date

Does NOT
---------
- Execute application queries
- Contain repository logic
"""

from __future__ import annotations

from pathlib import Path

from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.infrastructure.persistence.postgresql.session import (
    DatabaseSession,
)

logger = get_logger(__name__)


class SchemaManager:
    """
    Executes SQL migrations.

    Every *.sql file inside the migrations folder
    is executed in filename order.
    """

    def __init__(self):

        self.migrations_dir = (
            Path(__file__).parent
            / "migrations"
        )

    # ---------------------------------------------------------
    # Initialize Database
    # ---------------------------------------------------------

    def initialize(self) -> None:
        """
        Execute every SQL migration.
        """

        if not self.migrations_dir.exists():

            raise FileNotFoundError(
                f"Migration folder not found:\n{self.migrations_dir}"
            )

        migration_files = sorted(
            self.migrations_dir.glob("*.sql")
        )

        if not migration_files:

            logger.warning(
                "No migration files found."
            )

            return

        logger.info(
            "Applying %d migration(s)...",
            len(migration_files),
        )

        for file in migration_files:

            self._run_file(file)

        logger.info(
            "Database schema is up to date."
        )

    # ---------------------------------------------------------
    # Execute One Migration File
    # ---------------------------------------------------------

    def _run_file(self, file: Path) -> None:
      logger.info("Running migration: %s", file.name)

      sql = file.read_text(encoding="utf-8")

      with DatabaseSession() as session:
        cursor = session.cursor()
        cursor.execute(sql)
        cursor.close()

      logger.info("Finished migration: %s", file.name)