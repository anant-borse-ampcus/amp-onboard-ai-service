from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(AppException):
    """Raised when request or domain validation fails."""

    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
        )


class ConfigurationError(AppException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str = "Configuration error", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )


class RepositoryError(AppException):
    """Raised when a repository operation fails."""

    def __init__(self, message: str = "Repository operation failed", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_code="REPOSITORY_ERROR",
            details=details,
        )


class LLMProviderError(AppException):
    """Raised when an LLM provider operation fails."""

    def __init__(self, message: str = "LLM provider error", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=502,
            error_code="LLM_PROVIDER_ERROR",
            details=details,
        )
