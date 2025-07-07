"""Authentication middleware for Flask application."""

from flask import Flask, request, jsonify, current_app
from typing import Optional, List
from .jwt_service import JWTService
from .user_context import extract_user_context
from ..core.exceptions import AuthenticationError


class AuthenticationMiddleware:
    """Middleware to handle authentication for all routes."""
    
    def __init__(self, app: Optional[Flask] = None, public_paths: Optional[List[str]] = None):
        """Initialize authentication middleware.
        
        Args:
            app: Flask application instance
            public_paths: List of paths that don't require authentication
        """
        self.public_paths = public_paths or []
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize middleware with Flask app.
        
        Args:
            app: Flask application instance
        """
        app.before_request(self._authenticate_request)
    
    def _authenticate_request(self):
        """Authenticate incoming request."""
        # Skip authentication for public paths
        if self._is_public_path(request.path):
            return None
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return None
        
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'Missing authorization header'}), 401
            
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Invalid authorization header format'}), 401
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Validate token and extract user context
            jwt_service = current_app.config.get('jwt_service')
            if not jwt_service:
                current_app.logger.error("JWT service not configured")
                return jsonify({'error': 'Authentication service unavailable'}), 500
            
            user_context = extract_user_context(jwt_service, token)
            
            # Store user context in Flask g
            from flask import g
            g.current_user = user_context
            
            return None
            
        except AuthenticationError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            current_app.logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public and doesn't require authentication.
        
        Args:
            path: Request path
            
        Returns:
            True if path is public, False otherwise
        """
        # Always allow health check endpoint
        if path == '/health':
            return True
        
        # Check against configured public paths
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        
        return False
