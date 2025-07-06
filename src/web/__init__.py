"""Web application module."""

from .app import create_app
from .routes import papers_bp, api_bp

__all__ = [
    'create_app',
    'papers_bp',
    'api_bp'
]
