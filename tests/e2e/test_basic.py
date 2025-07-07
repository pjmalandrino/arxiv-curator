"""
Basic E2E test file using pytest-playwright
"""
import pytest
from playwright.sync_api import Page, expect


class TestBasicE2E:
    """Basic E2E tests"""
    
    def test_frontend_loads(self, page: Page):
        """Test that frontend loads"""
        page.goto('http://localhost:3000')
        
        # Frontend should either show content or redirect to Keycloak
        page.wait_for_timeout(2000)
        
        url = page.url
        if 'localhost:3000' in url:
            # Still on frontend, check for login button
            title = page.title()
            assert 'arxiv' in title.lower() or 'curator' in title.lower()
            print(f"Frontend loaded with title: {title}")
        elif 'auth/realms' in url:
            # Redirected to Keycloak
            assert 'arxiv-test' in url or 'arxiv-curator' in url
            print(f"Redirected to Keycloak login at: {url}")
        else:
            pytest.fail(f"Unexpected URL: {url}")
    
    def test_keycloak_realm_exists(self, page: Page):
        """Test that Keycloak realm is accessible"""
        page.goto('http://localhost:8081/realms/arxiv-test/.well-known/openid-configuration')
        
        # Should get a JSON response
        content = page.content()
        assert 'issuer' in content
        assert 'authorization_endpoint' in content
        print("✅ Keycloak realm is properly configured")
    
    def test_backend_health(self, page: Page):
        """Test that backend is healthy"""
        response = page.goto('http://localhost:5001/health')
        assert response.status == 200
        
        content = page.content()
        assert 'healthy' in content
        print("✅ Backend is healthy")
