"""
Persistence models.

Architecture v2.0 (Frozen)

These lightweight dataclasses represent database records.
Repositories convert database rows into these models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class EpisodeRecord:

    episode_id: str

    created_at: datetime

    user_request: str

    workflow_state: dict[str, Any]

    evaluation_score: float | None


@dataclass(slots=True)
class ReflectionRecord:

    reflection_id: str

    created_at: datetime

    lesson: str

    source: str

    score: float | None