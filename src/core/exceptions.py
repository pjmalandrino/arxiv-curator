"""Custom exceptions for the ArXiv Curator application."""


class ArxivCuratorError(Exception):
    """Base exception for all ArXiv Curator errors."""
    pass


class DatabaseError(ArxivCuratorError):
    """Raised when database operations fail."""
    pass


class ArxivClientError(ArxivCuratorError):
    """Raised when ArXiv API interactions fail."""
    pass


class SummarizationError(ArxivCuratorError):
    """Raised when paper summarization fails."""
    pass


class ConfigurationError(ArxivCuratorError):
    """Raised when configuration is invalid."""
    pass


class AuthenticationError(ArxivCuratorError):
    """Raised when authentication fails."""
    pass
