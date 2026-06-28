"""
Application initialization package.
"""

from .bootstrap import bootstrap_application
from .lifecycle import ApplicationLifecycle

__all__ = [
    "bootstrap_application",
    "ApplicationLifecycle",
]