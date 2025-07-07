"""JWT token validation service."""

import logging
from typing import Dict, Any, Optional
from jose import JWTError, jwt
import requests
from functools import lru_cache

from ..core.config import Config
from ..core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class JWTService:
    """Service for JWT token validation using Keycloak."""
    
    def __init__(self, config: Config):
        """Initialize JWT service.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.keycloak_url = config.keycloak.url
        self.realm = config.keycloak.realm
        self.client_id = config.keycloak.client_id
        self.algorithm = config.jwt_algorithm
        
    @lru_cache(maxsize=1)
    def get_public_keys(self) -> Dict[str, Any]:
        """Get Keycloak public keys for token validation.
        
        Returns:
            Dict containing public keys
            
        Raises:
            AuthenticationError: If keys cannot be retrieved
        """
        try:
            certs_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/certs"
            response = requests.get(certs_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get Keycloak public keys: {e}")
            raise AuthenticationError("Cannot retrieve authentication keys") from e
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return claims.
        
        Args:
            token: JWT token string
            
        Returns:
            Dict containing token claims
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Get public keys
            keys = self.get_public_keys()
            
            # Decode and validate token
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get('kid')
            
            if not key_id:
                raise AuthenticationError("Token missing key ID")
            
            # Find the correct key
            public_key = None
            for key in keys.get('keys', []):
                if key.get('kid') == key_id:
                    public_key = key
                    break
            
            if not public_key:
                raise AuthenticationError("Public key not found")
            
            # Validate token
            claims = jwt.decode(
                token,
                public_key,
                algorithms=[self.algorithm],
                audience=self.client_id,
                issuer=f"{self.keycloak_url}/realms/{self.realm}"
            )
            
            return claims
            
        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise AuthenticationError("Invalid token") from e
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise AuthenticationError("Token validation failed") from e
