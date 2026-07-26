"""
Tests for InformationService.

Architecture v2.3 (Frozen)
"""

from unittest.mock import Mock

from mobile_ai_system.application.services.information_service import (
    InformationService,
)

    
class DummyMemoryManager:

    def latest_episodes(self, limit=5):
        return [{"title": "Episode 1"}]

    def latest_reflections(self, limit=5):
        return [{"summary": "Reflection 1"}]




def test_collect_information():

    memory = DummyMemoryManager()

    service = InformationService(
        mongo_tool=Mock(),
        llm_tool=Mock(),
        web_tool=Mock(),
        memory_manager=memory,
    )

    state = {
        "user_request": "Analyze Verizon",
    }

    result = service.collect_information(state)

    assert result.query == "Analyze Verizon"

    assert "memory" in result.metadata

    memory_context = result.metadata["memory"]

    assert "episodes" in memory_context
    assert "reflections" in memory_context
    assert "working" in memory_context
    assert "semantic" in memory_context

    assert len(memory_context["episodes"]) == 1
    assert len(memory_context["reflections"]) == 1