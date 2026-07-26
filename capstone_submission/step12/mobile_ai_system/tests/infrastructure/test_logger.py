from mobile_ai_system.infrastructure.logging import (
    get_logger,
)


def test_logger():

    logger = get_logger(
        "test"
    )

    logger.info(
        "Hello Logger"
    )

    assert logger.name == "test"