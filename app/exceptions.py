class ApplicationError(Exception):
    """Base exception for application-specific errors."""

    pass


class ConfigurationError(ApplicationError):
    """Raised when application configuration is invalid."""

    pass


class LLMServiceError(ApplicationError):
    """Raised when the LLM service fails."""

    pass


class GuardrailError(ApplicationError):
    """Raised when a guardrail blocks a request."""

    pass
