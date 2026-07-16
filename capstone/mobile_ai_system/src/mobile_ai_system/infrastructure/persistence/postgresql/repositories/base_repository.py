from mobile_ai_system.infrastructure.persistence.postgresql.session import (
    DatabaseSession,
)

from mobile_ai_system.infrastructure.persistence.postgresql.client import (
    PostgreSQLClient,
)


class BaseRepository:
    """
    Base repository providing shared DB access utilities.
    """

    # ---------------------------------------------------------
    # Session
    # ---------------------------------------------------------

    def session(self):
        """
        Create a database session context manager.
        """
        return DatabaseSession()

    # ---------------------------------------------------------
    # Client
    # ---------------------------------------------------------

    def client(self, session):
        """
        Create a PostgreSQL client bound to a session.
        """
        return PostgreSQLClient(session)