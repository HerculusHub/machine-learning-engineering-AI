from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class MetadataState:
    """
    Request metadata.
    """

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    start_time: datetime = field(
        default_factory=datetime.utcnow
    )

    status: str = "running"