"""
Authentication Flow E2E Tests
"""
import pytest
from playwright.async_api import Page
from ..pages.login_page import LoginPage
from ..config.test_config import TestConfig


class TestAuthenticationFlow:
    """Test authentication workflows"""
    
    @pytest.mark.asyncio
    async def test_successful_login(self, page: Page, test_users):
        """Test successful login flow"""
        login_page = LoginPage(page)
        
        # Navigate to application
        await login_page.navigate()
        
        # Verify login button is visible
        assert await login_page.is_visible(login_page.LOGIN_BUTTON)
        
        # Perform login
        user = test_users['user']
        await login_page.login(user['username'], user['password'])
        
        # Verify successful login
        assert await login_page.is_logged_in()
        username = await login_page.get_username()
        assert user['username'] in username.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_credentials(self, page: Page, test_users):
        """Test login with invalid credentials"""
        login_page = LoginPage(page)
        
        await login_page.navigate()
        
        # Try to login with wrong password
        user = test_users['user']
        try:
            await login_page.login(user['username'], 'wrong_password')
        except:
            # Expected to fail
            pass
        
        # Should still be on Keycloak login page
        assert 'auth/realms' in page.url
        
        # Check for error message
        error_visible = await page.locator('.kc-feedback-text').is_visible()
        assert error_visible
        
    @pytest.mark.asyncio
    async def test_logout_flow(self, page: Page, test_users):
        """Test logout functionality"""
        login_page = LoginPage(page)
        
        # Login first
        await login_page.navigate()
        user = test_users['user']
        await login_page.login(user['username'], user['password'])
        
        # Verify logged in
        assert await login_page.is_logged_in()
        
        # Perform logout
        await login_page.logout()
        
        # Verify logged out
        assert not await login_page.is_logged_in()
        assert await login_page.is_visible(login_page.LOGIN_BUTTON)
    
    @pytest.mark.asyncio
    async def test_role_based_access(self, page: Page, test_users):
        """Test role-based access control"""
        login_page = LoginPage(page)
        
        # Test admin access
        await login_page.navigate()
        admin = test_users['admin']
        await login_page.login(admin['username'], admin['password'])
        
        # Check admin menu is visible
        admin_menu = await page.locator('[data-testid="admin-menu"]').is_visible()
        assert admin_menu
        
        await login_page.logout()
        
        # Test regular user access
        user = test_users['user']
        await login_page.login(user['username'], user['password'])
        
        # Admin menu should not be visible
        admin_menu = await page.locator('[data-testid="admin-menu"]').is_visible()
        assert not admin_menu
        
    @pytest.mark.asyncio
    async def test_session_persistence(self, page: Page, test_users):
        """Test session persists across page refreshes"""
        login_page = LoginPage(page)
        
        # Login
        await login_page.navigate()
        user = test_users['user']
        await login_page.login(user['username'], user['password'])
        
        # Refresh page
        await page.reload()
        
        # Should still be logged in
        assert await login_page.is_logged_in()
        username = await login_page.get_username()
        assert user['username'] in username.lower()
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, page: Page, test_users):
        """Test automatic token refresh"""
        login_page = LoginPage(page)
        
        # Login
        await login_page.navigate()
        user = test_users['user']
        await login_page.login(user['username'], user['password'])
        
        # Wait for initial token to be near expiry
        # (This would be configured for shorter times in test environment)
        await page.wait_for_timeout(5000)
        
        # Make an API call that should trigger token refresh
        await page.evaluate("""
            () => {
                return fetch('/api/papers', {
                    headers: {
                        'Accept': 'application/json'
                    },
                    credentials: 'include'
                });
            }
        """)
        
        # Should still be logged in
        assert await login_page.is_logged_in()
        
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, browser, test_users):
        """Test multiple concurrent sessions"""
        # Create two contexts (simulating different browsers)
        context1 = await browser.new_context()
        context2 = await browser.new_context()
        
        page1 = await context1.new_page()
        page2 = await context2.new_page()
        
        login_page1 = LoginPage(page1)
        login_page2 = LoginPage(page2)
        
        # Login with different users
        await login_page1.navigate()
        await login_page1.login(
            test_users['admin']['username'], 
            test_users['admin']['password']
        )
        
        await login_page2.navigate()
        await login_page2.login(
            test_users['user']['username'], 
            test_users['user']['password']
        )
        
        # Verify both sessions are independent
        assert await login_page1.is_logged_in()
        assert await login_page2.is_logged_in()
        
        username1 = await login_page1.get_username()
        username2 = await login_page2.get_username()
        
        assert test_users['admin']['username'] in username1.lower()
        assert test_users['user']['username'] in username2.lower()
        
        # Cleanup
        await context1.close()
        await context2.close()
