"""
Application entry point.
"""

from __future__ import annotations

from mobile_ai_system.application.lifecycle import (
    ApplicationLifecycle,
)

from mobile_ai_system.infrastructure.logging import (
    get_logger,
)


logger = get_logger(__name__)


def main() -> None:
    """
    Start the application.
    """

    app = ApplicationLifecycle()

    logger.info(
        "Initializing application..."
    )

    app.initialize()

    print()

    print("=" * 60)

    print(
        " Mobile AI Strategic Intelligence Platform "
    )

    print("=" * 60)

    print()

    print(
        "Type 'exit' to quit."
    )

    while True:

        user_input = input(
            "\nUser > "
        )

        if user_input.lower() == "exit":

            break

        print()

        print(
            "Supervisor not implemented yet."
        )

    logger.info(
        "Application shutting down..."
    )

    app.shutdown()


if __name__ == "__main__":

    main()