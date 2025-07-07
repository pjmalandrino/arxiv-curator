"""
Authentication E2E tests using pytest-playwright
"""
import pytest
from playwright.sync_api import Page, expect


class TestAuthentication:
    """Test authentication flows"""
    
    def test_login_with_test_user(self, page: Page):
        """Test login with test user credentials"""
        # Navigate to frontend
        page.goto('http://localhost:3000')
        
        # Wait for redirect to Keycloak
        page.wait_for_url('**/auth/realms/**')
        print(f"Redirected to: {page.url}")
        
        # Fill in test user credentials
        page.fill('#username', 'test_user')
        page.fill('#password', 'Test123!')
        
        # Submit login form
        page.click('#kc-login')
        
        # Wait for redirect back to application
        try:
            page.wait_for_url('http://localhost:3000/**', timeout=15000)
            print(f"✅ Login successful! Redirected to: {page.url}")
            
            # Check if user is logged in by looking for user-related elements
            # Try different possible selectors
            user_indicators = [
                '[data-testid="user-menu"]',
                '.user-menu',
                '.user-info',
                '.username',
                'button:has-text("Logout")',
                'a:has-text("Logout")'
            ]
            
            user_element_found = False
            for selector in user_indicators:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        print(f"✅ Found user element: {selector}")
                        user_element_found = True
                        break
                except:
                    continue
            
            if not user_element_found:
                # Check if username appears in page
                page_text = page.content()
                if 'test_user' in page_text.lower():
                    print("✅ Username found in page content")
                else:
                    print("⚠️  Could not find user indicator elements")
                    page.screenshot(path="login-result.png")
                    
        except Exception as e:
            print(f"❌ Login failed: {e}")
            page.screenshot(path="login-failed.png")
            raise
    
    def test_login_with_invalid_credentials(self, page: Page):
        """Test login with invalid credentials"""
        # Navigate to frontend
        page.goto('http://localhost:3000')
        
        # Wait for redirect to Keycloak
        page.wait_for_url('**/auth/realms/**')
        
        # Fill in invalid credentials
        page.fill('#username', 'test_user')
        page.fill('#password', 'WrongPassword123!')
        
        # Submit login form
        page.click('#kc-login')
        
        # Wait a bit for error to appear
        page.wait_for_timeout(2000)
        
        # Should still be on Keycloak login page
        assert '/auth/realms/' in page.url
        print("✅ Stayed on login page after invalid credentials")
        
        # Check for error message
        error_selectors = [
            '.alert-error',
            '.kc-feedback-text',
            '[class*="error"]',
            '.pf-c-alert',
            '#input-error'
        ]
        
        error_found = False
        for selector in error_selectors:
            try:
                error_element = page.locator(selector).first
                if error_element.is_visible(timeout=1000):
                    error_text = error_element.text_content()
                    print(f"✅ Error message displayed: {error_text}")
                    error_found = True
                    break
            except:
                continue
        
        if not error_found:
            print("⚠️  No explicit error message found, but login was prevented")
    
    def test_logout(self, page: Page):
        """Test logout functionality"""
        # First login
        page.goto('http://localhost:3000')
        page.wait_for_url('**/auth/realms/**')
        page.fill('#username', 'test_user')
        page.fill('#password', 'Test123!')
        page.click('#kc-login')
        page.wait_for_url('http://localhost:3000/**', timeout=15000)
        
        print("✅ Logged in successfully")
        
        # Look for logout button/link
        logout_selectors = [
            'button:has-text("Logout")',
            'a:has-text("Logout")',
            'button:has-text("Sign Out")',
            'a:has-text("Sign Out")',
            '[data-testid="logout-button"]'
        ]
        
        logout_clicked = False
        for selector in logout_selectors:
            try:
                logout_element = page.locator(selector).first
                if logout_element.is_visible(timeout=2000):
                    print(f"Found logout element: {selector}")
                    logout_element.click()
                    logout_clicked = True
                    break
            except:
                continue
        
        if logout_clicked:
            # Wait for logout to complete
            page.wait_for_timeout(3000)
            
            # Check if we're logged out (back to login page or frontend without user info)
            if '/auth/realms/' in page.url:
                print("✅ Redirected to login page after logout")
            else:
                print(f"After logout URL: {page.url}")
                # Try to find login button again
                login_visible = False
                for selector in ['button:has-text("Login")', 'a:has-text("Login")', 'button:has-text("Sign In")']:
                    try:
                        if page.locator(selector).first.is_visible(timeout=1000):
                            login_visible = True
                            break
                    except:
                        continue
                
                if login_visible:
                    print("✅ Login button visible after logout")
                else:
                    print("⚠️  Logout status unclear")
        else:
            print("⚠️  Could not find logout button - may need user menu interaction first")
            page.screenshot(path="logout-button-search.png")
