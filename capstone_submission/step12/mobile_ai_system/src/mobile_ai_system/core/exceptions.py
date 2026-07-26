"""
Custom project exceptions.
"""


class MobileAISystemError(Exception):
    """Base exception."""


class ConfigurationError(MobileAISystemError):
    """Configuration problem."""


class DatabaseConnectionError(MobileAISystemError):
    """Database unavailable."""


class RetrievalError(MobileAISystemError):
    """Information retrieval failed."""


class ModelInferenceError(MobileAISystemError):
    """ML prediction failed."""


class ReportGenerationError(MobileAISystemError):
    """Report generation failed."""


class EvaluationError(MobileAISystemError):
    """Evaluation failed."""