"""
Shared project types.

Only lightweight type aliases, TypedDicts, Protocols and enums
belong here.
"""

from __future__ import annotations

from typing import Any, TypedDict


JSON = dict[str, Any]


class HealthStatus(TypedDict):
    """
    Health check response.
    """

    component: str
    status: str
    details: str


class ServiceInfo(TypedDict):
    """
    Information stored about a registered service.
    """

    name: str
    initialized: bool
    