import pytest

from mobile_ai_system.agents.supervisor_agent import SupervisorAgent
from mobile_ai_system.agents.information_agent import InformationAgent
from mobile_ai_system.agents.impact_agent import ImpactAgent
from mobile_ai_system.agents.report_agent import ReportAgent
from mobile_ai_system.agents.evaluation_agent import EvaluationAgent

from mobile_ai_system.memory.memory_manager import MemoryManager
from mobile_ai_system.tools.tool_registry import ToolRegistry
from mobile_ai_system.tools.mongo_tool import MongoTool


@pytest.fixture
def tool_registry():
    registry = ToolRegistry()
    registry.register("mongo", MongoTool())
    return registry


@pytest.fixture
def memory():
    return MemoryManager()


@pytest.fixture
def agents(tool_registry, memory):

    return [
        SupervisorAgent(memory=memory, tools=tool_registry),
        InformationAgent(memory=memory, tools=tool_registry),
        ImpactAgent(memory=memory, tools=tool_registry),
        ReportAgent(memory=memory, tools=tool_registry),
        EvaluationAgent(memory=memory, tools=tool_registry),
    ]


@pytest.fixture
def base_state():
    return {
        "user_request": "Analyze Verizon impact report"
    }