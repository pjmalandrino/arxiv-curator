"""
Test Configuration
"""
import os
from typing import Optional


class TestConfig:
    """E2E Test Configuration"""
    
    # Browser settings
    HEADLESS: bool = os.getenv('E2E_HEADLESS', 'true').lower() == 'true'
    BROWSER: str = os.getenv('E2E_BROWSER', 'chromium')
    SLOW_MO: int = int(os.getenv('E2E_SLOW_MO', '0'))
    
    # Application URLs
    FRONTEND_URL: str = os.getenv('E2E_FRONTEND_URL', 'http://localhost:3000')
    API_BASE_URL: str = os.getenv('E2E_API_URL', 'http://localhost:5001')
    KEYCLOAK_URL: str = os.getenv('E2E_KEYCLOAK_URL', 'http://localhost:8081')
    
    # Keycloak configuration
    KEYCLOAK_REALM: str = os.getenv('E2E_KEYCLOAK_REALM', 'arxiv-test')
    KEYCLOAK_CLIENT_ID: str = os.getenv('E2E_KEYCLOAK_CLIENT_ID', 'arxiv-frontend')
    KEYCLOAK_ADMIN_USER: str = os.getenv('E2E_KEYCLOAK_ADMIN_USER', 'admin')
    KEYCLOAK_ADMIN_PASSWORD: str = os.getenv('E2E_KEYCLOAK_ADMIN_PASSWORD', 'test_admin')
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        'E2E_DATABASE_URL', 
        'postgresql://test_curator:test_password@localhost:5433/arxiv_test'
    )
    
    # Test timeouts (in milliseconds)
    DEFAULT_TIMEOUT: int = 30000
    NAVIGATION_TIMEOUT: int = 60000
    API_TIMEOUT: int = 10000
    
    # Test data
    TEST_USER_PASSWORD: str = 'Test123!'
    
    @classmethod
    def get_timeout(cls, timeout_type: str = 'default') -> int:
        """Get timeout value by type"""
        timeouts = {
            'default': cls.DEFAULT_TIMEOUT,
            'navigation': cls.NAVIGATION_TIMEOUT,
            'api': cls.API_TIMEOUT
        }
        return timeouts.get(timeout_type, cls.DEFAULT_TIMEOUT)
