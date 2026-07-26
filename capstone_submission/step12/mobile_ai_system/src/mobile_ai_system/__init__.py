"""
Mobile AI System

A multi-agent strategic intelligence platform for
Mobile Network Operators.
"""

from importlib.metadata import version

try:
    __version__ = version("mobile-ai-system")
except Exception:
    __version__ = "0.1.0"