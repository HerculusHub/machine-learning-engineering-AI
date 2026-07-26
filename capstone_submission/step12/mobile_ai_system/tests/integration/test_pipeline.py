# tests/integration/test_pipeline.py

from mobile_ai_system.orchestration.runner import run_pipeline
from mobile_ai_system.memory.memory_manager import MemoryManager


def test_pipeline(agents, base_state):

    memory = MemoryManager()

    result = run_pipeline(
        agents,
        base_state,
        memory,
    )

    assert result is not None