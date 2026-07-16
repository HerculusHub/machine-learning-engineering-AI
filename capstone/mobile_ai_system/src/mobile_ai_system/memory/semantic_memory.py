from copy import deepcopy
from collections import defaultdict
from typing import Any


class SemanticMemory:
    """
    Stores reusable knowledge.

    Backend:
        In-memory dictionary.

    Future:
        Vector Database.
    """

    def __init__(self):

        self._knowledge = defaultdict(list)

    def add(
        self,
        category: str,
        item: Any,
    ):

        self._knowledge[category].append(
            deepcopy(item)
        )

    def get(
        self,
        category: str,
    ):

        return deepcopy(
            self._knowledge.get(category, [])
        )

    def categories(self):

        return list(
            self._knowledge.keys()
        )

    def count(
        self,
        category: str | None = None,
    ):

        if category is None:

            return sum(
                len(v)
                for v in self._knowledge.values()
            )

        return len(
            self._knowledge.get(category, [])
        )

    def clear(self):

        self._knowledge.clear()