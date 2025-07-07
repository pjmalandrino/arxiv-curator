"""
Simple Authentication E2E Test
"""
import pytest
from playwright.async_api import async_playwright, Page
import asyncio


@pytest.mark.asyncio
async def test_login_flow():
    """Test the basic login flow"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the application
        await page.goto('http://localhost:3000')
        
        # Should redirect to Keycloak login
        await page.wait_for_url('**/auth/realms/**', timeout=10000)
        
        # Fill in credentials
        await page.fill('#username', 'test_user')
        await page.fill('#password', 'Test123!')
        
        # Click login button
        await page.click('#kc-login')
        
        # Should redirect back to application
        try:
            await page.wait_for_url('http://localhost:3000/**', timeout=15000)
            print("✅ Login successful!")
            
            # Take screenshot
            await page.screenshot(path="login-success.png")
            
            # Check if user menu is visible
            user_menu = await page.query_selector('[data-testid="user-menu"]')
            if user_menu:
                print("✅ User menu found")
            else:
                # Try alternative selectors
                user_info = await page.query_selector('.user-info, .user-menu, .username')
                if user_info:
                    print("✅ User info found")
                else:
                    print("⚠️  User menu not found, checking page content...")
                    content = await page.content()
                    if 'test_user' in content.lower():
                        print("✅ Username found in page")
                    else:
                        print("❌ Username not found in page")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            await page.screenshot(path="login-failed.png")
            raise
        
        await browser.close()


@pytest.mark.asyncio 
async def test_invalid_login():
    """Test login with invalid credentials"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the application
        await page.goto('http://localhost:3000')
        
        # Should redirect to Keycloak login
        await page.wait_for_url('**/auth/realms/**', timeout=10000)
        
        # Fill in wrong credentials
        await page.fill('#username', 'test_user')
        await page.fill('#password', 'wrong_password')
        
        # Click login button
        await page.click('#kc-login')
        
        # Should stay on Keycloak with error
        await asyncio.sleep(2)  # Wait for error to appear
        
        # Check if still on Keycloak
        current_url = page.url
        assert 'auth/realms' in current_url, "Should stay on Keycloak login page"
        
        # Check for error message
        error = await page.query_selector('.alert-error, .kc-feedback-text, [class*="error"]')
        if error:
            error_text = await error.text_content()
            print(f"✅ Error message shown: {error_text}")
        else:
            print("⚠️  No error message found, but stayed on login page")
        
        await browser.close()


if __name__ == "__main__":
    # Run tests directly
    asyncio.run(test_login_flow())
    asyncio.run(test_invalid_login())
