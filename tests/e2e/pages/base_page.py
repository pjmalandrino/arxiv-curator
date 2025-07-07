"""
Base Page Object
"""
from playwright.async_api import Page, Locator
from typing import Optional, Union
import asyncio


class BasePage:
    """Base class for all page objects"""
    
    def __init__(self, page: Page):
        self.page = page
        self.timeout = 30000  # 30 seconds default timeout
        
    async def navigate(self, url: str):
        """Navigate to URL"""
        await self.page.goto(url, wait_until='networkidle')
        
    async def wait_for_element(self, selector: str, 
                             state: str = 'visible',
                             timeout: Optional[int] = None) -> Locator:
        """Wait for element and return locator"""
        timeout = timeout or self.timeout
        locator = self.page.locator(selector)
        await locator.wait_for(state=state, timeout=timeout)
        return locator
    
    async def click_element(self, selector: str):
        """Click an element"""
        element = await self.wait_for_element(selector)
        await element.click()
        
    async def fill_input(self, selector: str, value: str):
        """Fill input field"""
        element = await self.wait_for_element(selector)
        await element.fill(value)
        
    async def get_text(self, selector: str) -> str:
        """Get element text"""
        element = await self.wait_for_element(selector)
        return await element.text_content()
        
    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        try:
            await self.wait_for_element(selector, timeout=5000)
            return True
        except:
            return False
            
    async def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None):
        """Wait for URL to match pattern"""
        timeout = timeout or self.timeout
        await self.page.wait_for_url(url_pattern, timeout=timeout)
