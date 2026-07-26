"""
Working Memory

Architecture v2.2 (Frozen)

Short-lived memory shared by agents during one workflow.

Not persisted.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class WorkingMemory:

    def __init__(self):

        self._store: dict[str, Any] = {}

        self._artifacts: dict[str, Any] = {}

    # ---------------------------------------------------------
    # Variables
    # ---------------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ):

        self._store[key] = value

    def get(
        self,
        key: str,
        default=None,
    ):

        return self._store.get(
            key,
            default,
        )

    def append(
        self,
        key: str,
        value: Any,
    ):

        if key not in self._store:

            self._store[key] = []

        self._store[key].append(value)

    # ---------------------------------------------------------
    # Artifacts
    # ---------------------------------------------------------

    def update_artifact(
        self,
        name: str,
        artifact: Any,
    ):

        self._artifacts[name] = artifact

    def get_artifact(
        self,
        name: str,
        default=None,
    ):

        return self._artifacts.get(
            name,
            default,
        )

    # ---------------------------------------------------------
    # Snapshot
    # ---------------------------------------------------------

    def snapshot(self):

        return {

            "memory": deepcopy(self._store),

            "artifacts": deepcopy(
                self._artifacts
            ),

        }

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self):

        self._store.clear()

        self._artifacts.clear()