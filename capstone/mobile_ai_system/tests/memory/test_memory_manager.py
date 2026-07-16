from mobile_ai_system.memory.memory_manager import (
    MemoryManager,
)


def test_memory_manager():

    manager = MemoryManager()

    assert manager.repositories is not None