"""
Simple debug test
"""
import asyncio
from playwright.async_api import async_playwright


async def check_frontend():
    """Check if frontend is accessible"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            
            print("Navigating to frontend...")
            response = await page.goto('http://localhost:3000', wait_until='domcontentloaded')
            print(f"Status: {response.status}")
            
            # Wait a moment
            await page.wait_for_timeout(2000)
            
            # Check current URL
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Get page title
            title = await page.title()
            print(f"Title: {title}")
            
            # Take screenshot
            await page.screenshot(path="frontend-check.png")
            
            # Check for specific elements
            if 'keycloak' in current_url or 'auth' in current_url:
                print("✅ Already redirected to Keycloak")
            else:
                print("Looking for login elements...")
                # Try to find any login-related element
                selectors = [
                    'button:has-text("Login")',
                    'button:has-text("Sign In")', 
                    'a:has-text("Login")',
                    'a:has-text("Sign In")',
                    '[data-testid="login-button"]',
                    '.login-button',
                    '#login-button'
                ]
                
                for selector in selectors:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"Found element with selector: {selector}")
                        await element.click()
                        await page.wait_for_timeout(3000)
                        print(f"After click URL: {page.url}")
                        break
                else:
                    print("No login element found")
                    
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(check_frontend())
