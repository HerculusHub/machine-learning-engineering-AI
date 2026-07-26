from abc import ABC, abstractmethod


class BaseAgent(ABC):

    def __init__(self, memory=None, tools=None):
        self.memory = memory
        self.tools = tools or {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name"""
        pass

    @abstractmethod
    def run(self, state: dict) -> dict:
        """Execute agent logic"""
        pass


