from __future__ import annotations

from typing import Any

from mobile_ai_system.tools.mongo_tool import MongoTool
from mobile_ai_system.tools.postgres_tool import PostgreSQLTool
from mobile_ai_system.tools.vector_tool import VectorTool
from mobile_ai_system.tools.web_tool import WebTool
from mobile_ai_system.tools.llm_tool import LLMTool


class ToolRegistry:
    """
    Registry of tools available to agents.

    For the MVP, built-in tools are registered automatically.
    """

    def __init__(self) -> None:

        self._tools: dict[str, Any] = {}

        self._register_default_tools()

    # ---------------------------------------------------------
    # Default tools
    # ---------------------------------------------------------

    def _register_default_tools(self) -> None:

        self.register("mongo", MongoTool())
        self.register("postgres", PostgreSQLTool())
        self.register("vector", VectorTool())
        self.register("web", WebTool())
        self.register("llm", LLMTool())

    # ---------------------------------------------------------
    # Register
    # ---------------------------------------------------------

    def register(
        self,
        name: str,
        tool: Any,
    ) -> None:

        self._tools[name] = tool

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Any:

        return self._tools.get(name)

    # ---------------------------------------------------------
    # List
    # ---------------------------------------------------------

    def list_tools(self) -> list[str]:

        return sorted(self._tools.keys())

    # ---------------------------------------------------------
    # All
    # ---------------------------------------------------------

    def all(self) -> dict[str, Any]:

        return dict(self._tools)

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:

        self._tools.clear()