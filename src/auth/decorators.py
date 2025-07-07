"""Authentication decorators."""

from functools import wraps
from typing import List, Optional, Callable
from flask import request, g, current_app, jsonify

from .jwt_service import JWTService
from .user_context import extract_user_context
from ..core.exceptions import AuthenticationError


def get_jwt_service() -> JWTService:
    """Get JWT service from app config."""
    return current_app.config.get('jwt_service')


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for a route.
    
    Args:
        f: Route function to protect
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'Missing authorization header'}), 401
            
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Invalid authorization header format'}), 401
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Validate token and extract user context
            jwt_service = get_jwt_service()
            user_context = extract_user_context(jwt_service, token)
            
            # Store user context in Flask g
            g.current_user = user_context
            
            return f(*args, **kwargs)
            
        except AuthenticationError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            current_app.logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function


def require_role(required_roles: List[str]) -> Callable:
    """Decorator to require specific roles for a route.
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user = g.current_user
            
            # Check if user has any of the required roles
            if not any(user.has_role(role) for role in required_roles):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def require_admin(f: Callable) -> Callable:
    """Decorator to require admin role.
    
    Args:
        f: Route function to protect
        
    Returns:
        Decorated function
    """
    return require_role(['admin'])(f)
