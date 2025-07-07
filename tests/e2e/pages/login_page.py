"""
Login Page Object
"""
from .base_page import BasePage
from ..config.test_config import TestConfig


class LoginPage(BasePage):
    """Login page interactions"""
    
    def __init__(self, page):
        super().__init__(page)
        self.url = TestConfig.FRONTEND_URL
        
    # Selectors
    LOGIN_BUTTON = '[data-testid="login-button"]'
    LOGOUT_BUTTON = '[data-testid="logout-button"]'
    USER_MENU = '[data-testid="user-menu"]'
    USERNAME_INPUT = '#username'
    PASSWORD_INPUT = '#password'
    KEYCLOAK_LOGIN_BUTTON = '#kc-login'
    ERROR_MESSAGE = '.alert-error'
    
    async def navigate(self):
        """Navigate to application"""
        await super().navigate(self.url)
        
    async def login(self, username: str, password: str):
        """Complete login flow"""
        # Click login button
        await self.click_element(self.LOGIN_BUTTON)
        
        # Wait for Keycloak redirect
        await self.page.wait_for_url('**/auth/realms/**', timeout=10000)
        
        # Fill credentials
        await self.fill_input(self.USERNAME_INPUT, username)
        await self.fill_input(self.PASSWORD_INPUT, password)
        
        # Submit form
        await self.click_element(self.KEYCLOAK_LOGIN_BUTTON)
        
        # Wait for redirect back to application
        await self.page.wait_for_url(self.url + '/**', timeout=15000)
        
        # Verify login success
        await self.wait_for_element(self.USER_MENU)
    
    async def logout(self):
        """Logout from application"""
        # Click user menu
        await self.click_element(self.USER_MENU)
        
        # Click logout
        await self.click_element(self.LOGOUT_BUTTON)
        
        # Wait for redirect
        await self.page.wait_for_url(self.url, timeout=10000)
        
        # Verify logout
        await self.wait_for_element(self.LOGIN_BUTTON)
        
    async def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return await self.is_visible(self.USER_MENU)
        
    async def get_username(self) -> str:
        """Get logged in username"""
        if await self.is_logged_in():
            return await self.get_text(self.USER_MENU)
        return None
        
    async def get_error_message(self) -> str:
        """Get login error message"""
        if await self.is_visible(self.ERROR_MESSAGE):
            return await self.get_text(self.ERROR_MESSAGE)
        return None
