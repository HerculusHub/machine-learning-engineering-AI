
"""
Simple dependency injection container.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


Factory = Callable[[], Any]


class ServiceContainer:

    def __init__(self):

        self._instances: dict[str, Any] = {}

        self._factories: dict[str, Factory] = {}

    # -------------------------

    def register_instance(
        self,
        name: str,
        instance: Any,
    ) -> None:

        self._instances[name] = instance

    # -------------------------

    def register_factory(
        self,
        name: str,
        factory: Factory,
    ) -> None:

        self._factories[name] = factory

    # -------------------------

    def resolve(
        self,
        name: str,
    ) -> Any:

        if name in self._instances:

            return self._instances[name]

        if name in self._factories:

            instance = self._factories[name]()

            self._instances[name] = instance

            return instance

        raise KeyError(
            f"Service '{name}' is not registered."
        )

    # -------------------------

    def contains(
        self,
        name: str,
    ) -> bool:

        return (
            name in self._instances
            or
            name in self._factories
        )

    # -------------------------

    def clear(self) -> None:

        self._instances.clear()

        self._factories.clear()