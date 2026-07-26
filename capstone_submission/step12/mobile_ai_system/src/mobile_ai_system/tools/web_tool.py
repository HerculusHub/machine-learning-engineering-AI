"""
Web Tool

Architecture v2.3 (Frozen)

Provides web search capability.
"""

from __future__ import annotations

from mobile_ai_system.tools.base import BaseTool


class WebTool(BaseTool):
    """
    Tool wrapper for web search.

    Actual web search integration will be implemented
    later (SerpAPI, Tavily, Exa, Bing, etc.).
    """

    NAME = "web"

    def __init__(self) -> None:

        self._connected = False

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    
    def name(self):
        return "WebTool"

    def health_check(self):
        return True

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to the web search service.
        """

        self._connected = True

    def health_check(self) -> bool:
        return True
    
    # ---------------------------------------------------------
    # Execute
    # ---------------------------------------------------------

    def execute(
        self,
        query: str,
        limit: int = 10,
    ):
        """
        Standard execution entry point.
        """

        if not self._connected:

            self.connect()

        return self.search(
            query=query,
            limit=limit,
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        limit: int = 10,
    ):
        """
        Placeholder implementation.
        """

        raise NotImplementedError(
            "Web search integration is not implemented yet."
        )