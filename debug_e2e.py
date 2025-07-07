"""
Debug E2E Test - Check what's happening
"""
import asyncio
from playwright.async_api import async_playwright


async def debug_frontend():
    """Debug what's happening with the frontend"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run with UI
        page = await browser.new_page()
        
        print("Navigating to http://localhost:3000...")
        response = await page.goto('http://localhost:3000')
        print(f"Response status: {response.status}")
        
        # Wait a bit and check the URL
        await asyncio.sleep(3)
        print(f"Current URL: {page.url}")
        
        # Get page content
        title = await page.title()
        print(f"Page title: {title}")
        
        # Check for any login button
        login_button = await page.query_selector('button:has-text("Login"), button:has-text("Sign In"), [data-testid="login-button"], a:has-text("Login"), a:has-text("Sign In")')
        if login_button:
            print("Found login button, clicking...")
            await login_button.click()
            
            # Wait for navigation
            await asyncio.sleep(3)
            print(f"URL after click: {page.url}")
        else:
            print("No login button found")
            
            # Check page content
            content = await page.content()
            if 'keycloak' in content.lower():
                print("Page mentions Keycloak")
            if 'loading' in content.lower():
                print("Page shows loading...")
            
            # Take screenshot
            await page.screenshot(path="debug-frontend.png")
            print("Screenshot saved to debug-frontend.png")
        
        input("Press Enter to close browser...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_frontend())
