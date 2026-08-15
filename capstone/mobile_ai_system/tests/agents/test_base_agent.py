"""
Tests for BaseAgent.
"""

import pytest

from mobile_ai_system.agents.base_agent import BaseAgent
from mobile_ai_system.application.models.pipeline_context import (
    PipelineContext,
)


class DummyAgent(BaseAgent):

    @property
    def name(self):
        return "Dummy"

    def execute(self, context):
        context.metadata["dummy"] = True
        return context


def test_dummy_agent_execute():

    agent = DummyAgent()

    context = PipelineContext()

    result = agent.execute(context)

    assert result.metadata["dummy"] is True


def test_dummy_agent_name():

    agent = DummyAgent()

    assert agent.name == "Dummy"


def test_base_agent_is_abstract():

    with pytest.raises(TypeError):
        BaseAgent()