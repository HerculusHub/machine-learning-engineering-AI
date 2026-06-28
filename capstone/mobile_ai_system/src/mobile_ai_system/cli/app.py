"""
Application entry point.
"""

from mobile_ai_system.infrastructure.logging import get_logger


logger = get_logger(__name__)


def main() -> None:

    print()

    print("=" * 60)

    print(
        "Mobile AI Strategic Intelligence Platform"
    )

    print("=" * 60)

    logger.info(
        "Application started."
    )

    while True:

        query = input("\nUser> ")

        if query.lower() in {

            "quit",

            "exit"

        }:

            logger.info(
                "Application closed."
            )

            break

        print()

        print(
            "Supervisor not implemented yet."
        )


if __name__ == "__main__":

    main()