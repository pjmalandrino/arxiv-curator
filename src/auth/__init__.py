"""Authentication module."""

from .jwt_service import JWTService
from .decorators import require_auth, require_role, require_admin
from .user_context import UserContext, get_current_user, extract_user_context
from .middleware import AuthenticationMiddleware

__all__ = [
    'JWTService',
    'require_auth',
    'require_role',
    'require_admin',
    'UserContext',
    'get_current_user',
    'extract_user_context',
    'AuthenticationMiddleware'
]
