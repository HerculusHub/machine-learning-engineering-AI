def test_request_pipeline(container):

    information_service = container.resolve(
        "information_service"
    )

    assert information_service is not None

    supervisor = container.resolve(
        "supervisor_agent"
    )

    assert supervisor is not None