"""
Pipeline Runner

Architecture v2.3 (Frozen)

Responsibilities
----------------
- Execute the agent pipeline
- Initialize runtime state
- Attach shared runtime services
- Persist completed workflow into episodic memory
"""

from __future__ import annotations

from mobile_ai_system.infrastructure.logging.logger import get_logger
from mobile_ai_system.memory.memory_manager import MemoryManager
from mobile_ai_system.workspace.workspace import Workspace

logger = get_logger(__name__)


def run_pipeline(
    agents,
    state: dict,
    memory: MemoryManager,
):
    """
    Execute one complete workflow.
    """

    logger.info("========== Pipeline Started ==========")

    # -------------------------------------------------
    # Shared Runtime Objects
    # -------------------------------------------------

    state["memory"] = memory

    # Every execution receives a fresh workspace.
    state["workspace"] = Workspace()

    logger.info(
        "Initial state keys: %s",
        list(state.keys()),
    )

    # -------------------------------------------------
    # Execute Agents
    # -------------------------------------------------

    for index, agent in enumerate(agents, start=1):

        logger.info(
            "[Step %d/%d] Running %s",
            index,
            len(agents),
            agent.name,
        )

        state = agent.run(state)

        logger.info(
            "[Step %d/%d] %s completed",
            index,
            len(agents),
            agent.name,
        )

    logger.info("========== Pipeline Finished ==========")

    # -------------------------------------------------
    # Save Episode
    # -------------------------------------------------

    workflow_state = {
        "task_list": state.get("task_list"),
        "retrieved_events": state.get("retrieved_events"),
        "impact_result": state.get("impact_result"),
        "report": state.get("report"),
        "reflections": state.get("reflections", []),
    }

    episode_id = memory.save_episode(
        user_request=state.get("user_request", ""),
        workflow_state=workflow_state,
        evaluation_score=state.get("evaluation_score"),
    )

    logger.info(
        "Episode saved: %s",
        episode_id,
    )

    return state