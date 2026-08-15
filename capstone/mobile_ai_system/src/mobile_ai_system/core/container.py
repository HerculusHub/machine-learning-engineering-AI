"""
Dependency Injection Container

Architecture v2.3 (Frozen MVP)
"""

from __future__ import annotations

from typing import Any
from collections.abc import Callable


class Container:
    """
    Lightweight dependency injection container.

    Supports:

    - singleton instances
    - lazy factories

    without requiring third-party frameworks.
    """

    def __init__(self):

        self._services: dict[str, Any] = {}

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register_instance(
        self,
        name: str,
        instance: Any,
    ) -> None:

        self._services[name] = instance

    def register_factory(
        self,
        name: str,
        factory: Callable[[], Any],
    ) -> None:

        self._services[name] = factory

    # ---------------------------------------------------------
    # Resolution
    # ---------------------------------------------------------

    def resolve(
        self,
        name: str,
    ) -> Any:

        service = self._services[name]

        if callable(service):
            return service()

        return service

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def contains(
        self,
        name: str,
    ) -> bool:

        return name in self._services

    def registered_services(
        self,
    ) -> list[str]:

        return sorted(self._services.keys())