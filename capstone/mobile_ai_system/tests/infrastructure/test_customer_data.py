from mobile_ai_system.infrastructure.persistence.csv import (
    CustomerDataClient,
)


def test_load():

    client = CustomerDataClient()

    df = client.load()

    assert len(df) > 0


def test_columns():

    client = CustomerDataClient()

    cols = client.columns()

    assert len(cols) > 0