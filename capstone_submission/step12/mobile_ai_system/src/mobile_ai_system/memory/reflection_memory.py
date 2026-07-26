from copy import deepcopy
from datetime import datetime
from uuid import uuid4


class ReflectionMemory:
    """
    Stores lessons learned from previous workflows.

    Future backend:
        PostgreSQL
    """

    def __init__(self):

        self._reflections = []

    def add(
        self,
        lesson: str,
        source: str = "evaluation",
        score: float | None = None,
    ) -> str:

        reflection = {

            "reflection_id": str(uuid4()),

            "timestamp": datetime.utcnow().isoformat(),

            "lesson": lesson,

            "source": source,

            "score": score
        }

        self._reflections.append(
            reflection
        )

        return reflection["reflection_id"]

    def latest(
        self,
        n: int = 5,
    ):

        return deepcopy(
            self._reflections[-n:]
        )

    def all(self):

        return deepcopy(
            self._reflections
        )

    def count(self):

        return len(
            self._reflections
        )

    def clear(self):

        self._reflections.clear()