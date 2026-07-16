from mobile_ai_system.infrastructure.logging.logger import get_logger

from mobile_ai_system.memory.memory_manager import MemoryManager

from mobile_ai_system.workspace.workspace import Workspace


logger = get_logger(__name__)


def run_pipeline(
    agents,
    state,
    memory: MemoryManager,
):

    logger.info("========== Pipeline Started ==========")

    # -------------------------------------------------
    # Attach shared objects
    # -------------------------------------------------

    state["memory"] = memory

    if "workspace" not in state:
        state["workspace"] = Workspace()

    logger.info(
        "Initial state keys: %s",
        list(state.keys()),
    )

    # -------------------------------------------------
    # Execute agents
    # -------------------------------------------------

    for i, agent in enumerate(agents, start=1):

        logger.info(
            "[Step %d/%d] Running %s",
            i,
            len(agents),
            agent.name,
        )

        state = agent.run(state)

        logger.info(
            "[Step %d/%d] %s completed",
            i,
            len(agents),
            agent.name,
        )

    logger.info("========== Pipeline Finished ==========")

    # -------------------------------------------------
    # Save episode
    # -------------------------------------------------

    workflow_state = {

        "task_list": state.get("task_list"),

        "retrieved_events": state.get("retrieved_events"),

        "impact_result": state.get("impact_result"),

        "report": state.get("report"),

        "reflections": state.get(
            "reflections",
            [],
        ),

    }

    memory.save_episode(

        user_request=state.get(
            "user_request",
            "",
        ),

        workflow_state=workflow_state,

    )

    logger.info("Episode saved.")

    return state