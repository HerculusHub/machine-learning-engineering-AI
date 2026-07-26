
from mobile_ai_system.infrastructure.logging.logger import get_logger

from .base_agent import BaseAgent

logger = get_logger(__name__)


class ImpactAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "ImpactAgent"

    def run(self, state):

        logger.info("%s started", self.name)

        # -------------------------------------------------
        # Read retrieved events
        # -------------------------------------------------

        events = state.get("retrieved_events", [])

        if events is None:
            events = []

        logger.info(
            "Processing %d retrieved events",
            len(events),
        )

        # -------------------------------------------------
        # Compute simple impact score
        # -------------------------------------------------

        impact_score = sum(
            event.get("impact_score", 0.0)
            for event in events
            if isinstance(event, dict)
        )

        # -------------------------------------------------
        # Store result
        # -------------------------------------------------

        state["impact_result"] = {
            "total_impact_score": impact_score,
            "event_count": len(events),
        }

        logger.info(
            "Computed impact score: %.2f from %d events",
            impact_score,
            len(events),
        )

        logger.info("%s finished", self.name)

        return state