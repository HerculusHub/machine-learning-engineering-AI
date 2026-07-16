"""
Shared Workspace

Architecture v2.3 (Frozen)

Acts as the communication channel between agents.
"""

from __future__ import annotations

from copy import deepcopy


class Workspace:

    def __init__(self):

        self._data = {

            "information": {},

            "analysis": {},

            "report": {},

            "evaluation": {},

            "artifacts": {},
        }

    # ---------------------------------------------------------
    # Generic Access
    # ---------------------------------------------------------

    def get(self, section: str):

        return deepcopy(
            self._data.get(section, {})
        )

    def update(
        self,
        section: str,
        values: dict,
    ):

        self._data.setdefault(
            section,
            {},
        ).update(values)

    # ---------------------------------------------------------
    # Artifact Support
    # ---------------------------------------------------------

    def add_artifact(
        self,
        name: str,
        value,
    ):

        self._data["artifacts"][name] = value

    def artifact(
        self,
        name: str,
    ):

        return self._data["artifacts"].get(name)

    # ---------------------------------------------------------
    # Snapshot
    # ---------------------------------------------------------

    def snapshot(self):

        return deepcopy(self._data)

    def clear(self):

        for key in self._data:

            self._data[key].clear()