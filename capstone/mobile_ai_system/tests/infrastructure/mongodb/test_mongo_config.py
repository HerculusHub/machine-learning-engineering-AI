"""
Tests for MongoConfig

Architecture v2.3 (Frozen MVP)
"""

from mobile_ai_system.infrastructure.persistence.mongodb.mongo_config import (
    MongoConfig,
)


class DummySettings:
    """
    Fake settings object for unit testing.
    """

    mongo_uri = "mongodb://localhost:27017"

    mongo_database = "industry_db"

    mongo_collection = "operator_events"


def test_create_config():

    config = MongoConfig.from_settings(
        DummySettings(),
    )

    assert config.connection_string == (
        "mongodb://localhost:27017"
    )

    assert config.database_name == (
        "industry_db"
    )

    assert config.collection_name == (
        "operator_events"
    )


def test_connection_string():

    config = MongoConfig(

        connection_string="mongodb://server",

        database_name="db",

        collection_name="events",
    )

    assert config.connection_string == (
        "mongodb://server"
    )


def test_database_name():

    config = MongoConfig(

        connection_string="mongodb://server",

        database_name="industry",

        collection_name="events",
    )

    assert config.database_name == (
        "industry"
    )


def test_collection_name():

    config = MongoConfig(

        connection_string="mongodb://server",

        database_name="industry",

        collection_name="operator_events",
    )

    assert config.collection_name == (
        "operator_events"
    )


def test_multiple_instances_are_independent():

    config1 = MongoConfig(

        connection_string="mongodb://one",

        database_name="db1",

        collection_name="c1",
    )

    config2 = MongoConfig(

        connection_string="mongodb://two",

        database_name="db2",

        collection_name="c2",
    )

    assert config1.connection_string != config2.connection_string

    assert config1.database_name != config2.database_name

    assert config1.collection_name != config2.collection_name


def test_from_settings_returns_new_instance():

    config1 = MongoConfig.from_settings(
        DummySettings(),
    )

    config2 = MongoConfig.from_settings(
        DummySettings(),
    )

    assert config1 is not config2