"""User context management."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from flask import g, request

from .jwt_service import JWTService
from ..core.exceptions import AuthenticationError


@dataclass
class UserContext:
    """User context information."""
    
    user_id: str
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    raw_claims: Dict[str, Any]
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions
    
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return 'admin' in self.roles


def get_current_user() -> Optional[UserContext]:
    """Get current user from Flask context."""
    return getattr(g, 'current_user', None)


def extract_user_context(jwt_service: JWTService, token: str) -> UserContext:
    """Extract user context from JWT token.
    
    Args:
        jwt_service: JWT validation service
        token: JWT token string
        
    Returns:
        UserContext with user information
        
    Raises:
        AuthenticationError: If token is invalid
    """
    claims = jwt_service.validate_token(token)
    
    # Extract user information from claims
    user_id = claims.get('sub')
    username = claims.get('preferred_username', '')
    email = claims.get('email', '')
    
    # Extract roles
    realm_access = claims.get('realm_access', {})
    resource_access = claims.get('resource_access', {})
    roles = realm_access.get('roles', [])
    
    # Extract client-specific roles
    client_roles = resource_access.get('arxiv-backend', {}).get('roles', [])
    roles.extend(client_roles)
    
    # For now, permissions are same as roles
    # This can be extended with more sophisticated permission mapping
    permissions = roles.copy()
    
    return UserContext(
        user_id=user_id,
        username=username,
        email=email,
        roles=roles,
        permissions=permissions,
        raw_claims=claims
    )
