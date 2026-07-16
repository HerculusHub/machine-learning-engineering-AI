"""
Custom PostgreSQL exceptions.
"""


class PostgreSQLException(Exception):
    """Base exception for PostgreSQL persistence."""


class SchemaInitializationError(PostgreSQLException):
    """Raised when database schema initialization fails."""


class RepositoryError(PostgreSQLException):
    """Raised when repository operations fail."""


class ConnectionPoolError(PostgreSQLException):
    """Raised when a database connection cannot be acquired."""