"""
Tests for MongoClientManager

Architecture v2.3 (Frozen MVP)
"""

from unittest.mock import MagicMock
from unittest.mock import patch

from mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager import (
    MongoClientManager,
)


# ---------------------------------------------------------
# Constructor
# ---------------------------------------------------------

@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager.MongoClient"
)
def test_client_created(mock_client):

    manager = MongoClientManager(
        connection_string="mongodb://localhost:27017",
    )

    mock_client.assert_called_once_with(
        "mongodb://localhost:27017",
        serverSelectionTimeoutMS=5000,
    )

    assert manager.client is mock_client.return_value


# ---------------------------------------------------------
# database()
# ---------------------------------------------------------

@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager.MongoClient"
)
def test_database(mock_client):

    client = mock_client.return_value

    database = MagicMock()

    client.__getitem__.return_value = database

    manager = MongoClientManager(
        "mongodb://localhost",
    )

    result = manager.database(
        "industry_db",
    )

    client.__getitem__.assert_called_once_with(
        "industry_db",
    )

    assert result is database


# ---------------------------------------------------------
# collection()
# ---------------------------------------------------------

@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager.MongoClient"
)
def test_collection(mock_client):

    client = mock_client.return_value

    database = MagicMock()

    collection = MagicMock()

    client.__getitem__.return_value = database

    database.__getitem__.return_value = collection

    manager = MongoClientManager(
        "mongodb://localhost",
    )

    result = manager.collection(
        "industry_db",
        "operator_events",
    )

    client.__getitem__.assert_called_once_with(
        "industry_db",
    )

    database.__getitem__.assert_called_once_with(
        "operator_events",
    )

    assert result is collection


# ---------------------------------------------------------
# close()
# ---------------------------------------------------------

@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager.MongoClient"
)
def test_close(mock_client):

    client = mock_client.return_value

    manager = MongoClientManager(
        "mongodb://localhost",
    )

    manager.close()

    client.close.assert_called_once()


# ---------------------------------------------------------
# client property
# ---------------------------------------------------------

@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager.MongoClient"
)
def test_client_property(mock_client):

    manager = MongoClientManager(
        "mongodb://localhost",
    )

    assert manager.client is mock_client.return_value


# ---------------------------------------------------------
# multiple database calls
# ---------------------------------------------------------

@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.mongo_client_manager.MongoClient"
)
def test_database_returns_same_object(mock_client):

    client = mock_client.return_value

    database = MagicMock()

    client.__getitem__.return_value = database

    manager = MongoClientManager(
        "mongodb://localhost",
    )

    db1 = manager.database(
        "industry_db",
    )

    db2 = manager.database(
        "industry_db",
    )

    assert db1 is db2