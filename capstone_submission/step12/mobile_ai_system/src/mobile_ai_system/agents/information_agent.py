from mobile_ai_system.infrastructure.logging.logger import get_logger

from .base_agent import BaseAgent

logger = get_logger(__name__)


class InformationAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "InformationAgent"

    def run(self, state):

        logger.info("%s started", self.name)

        # -------------------------------------------------
        # Read request
        # -------------------------------------------------

        query = state.get("user_request", "")

        # -------------------------------------------------
        # Retrieve Mongo tool
        # -------------------------------------------------

        mongo = self.tools.get("mongo")

        if mongo is None:

            logger.warning(
                "MongoTool is not registered."
            )

            state["retrieved_events"] = []

            return state

        logger.info(
            "Searching MongoDB with query: %s",
            query,
        )

        # -------------------------------------------------
        # Retrieve events
        # -------------------------------------------------

        results = mongo.search_events(query)

        if results is None:

            results = []

        state["retrieved_events"] = results

        logger.info(
            "Retrieved %d events from MongoDB",
            len(results),
        )

        logger.info("%s finished", self.name)

        return state