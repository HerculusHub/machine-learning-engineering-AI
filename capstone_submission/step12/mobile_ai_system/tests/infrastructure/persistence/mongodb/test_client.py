from unittest.mock import MagicMock
from unittest.mock import patch

from mobile_ai_system.infrastructure.persistence.mongodb.client import (
    MongoDBClient,
)


@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.client.MongoClient"
)
def test_health_check_success(mock_client):

    # Mock MongoDB admin.ping()
    mock_instance = MagicMock()

    mock_instance.admin.command.return_value = {"ok": 1}

    mock_client.return_value = mock_instance

    mongo = MongoDBClient()

    assert mongo.health_check() is True


@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.client.MongoClient"
)
def test_search_events(mock_client):

    fake_collection = MagicMock()

    fake_collection.find.return_value.limit.return_value = [
        {"operator": "AT&T"},
        {"operator": "Verizon"},
    ]

    mock_db = MagicMock()

    mock_db.__getitem__.return_value = fake_collection

    mock_instance = MagicMock()

    mock_instance.__getitem__.return_value = fake_collection

    mock_client.return_value = mock_instance

    mongo = MongoDBClient()

    mongo.db = mock_db

    results = mongo.search_events(
        "Unlimited Plan"
    )

    assert len(results) == 2

    assert results[0]["operator"] == "AT&T"


@patch(
    "mobile_ai_system.infrastructure.persistence.mongodb.client.MongoClient"
)
def test_close(mock_client):

    mock_instance = MagicMock()

    mock_client.return_value = mock_instance

    mongo = MongoDBClient()

    mongo.close()

    mock_instance.close.assert_called_once()