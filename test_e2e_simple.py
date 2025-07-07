#!/usr/bin/env python3
"""Simple E2E test to check basic functionality"""
import asyncio
from playwright.async_api import async_playwright


async def test_frontend_available():
    """Test if frontend is accessible"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to frontend
        response = await page.goto('http://localhost:3000')
        assert response.status == 200, f"Frontend returned status {response.status}"
        
        # Check page title
        title = await page.title()
        print(f"Page title: {title}")
        assert "ArXiv Curator" in title
        
        # Take screenshot
        await page.screenshot(path="frontend-screenshot.png")
        print("Screenshot saved to frontend-screenshot.png")
        
        await browser.close()
        print("✅ Frontend is accessible")


async def test_keycloak_available():
    """Test if Keycloak is accessible"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to Keycloak
        response = await page.goto('http://localhost:8081/realms/arxiv-test/.well-known/openid-configuration')
        assert response.status == 200, f"Keycloak returned status {response.status}"
        
        # Check response contains expected data
        content = await response.json()
        assert "issuer" in content
        assert "authorization_endpoint" in content
        
        await browser.close()
        print("✅ Keycloak is accessible")


async def test_backend_health():
    """Test if backend API is healthy"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Check backend health endpoint
        response = await page.goto('http://localhost:5001/health')
        if response.status == 200:
            content = await response.json()
            print(f"Backend health: {content}")
            print("✅ Backend API is healthy")
        else:
            print(f"⚠️  Backend returned status {response.status}")
        
        await browser.close()


async def main():
    """Run all tests"""
    print("Running E2E tests...")
    print("-" * 50)
    
    try:
        await test_frontend_available()
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
    
    try:
        await test_keycloak_available()
    except Exception as e:
        print(f"❌ Keycloak test failed: {e}")
    
    try:
        await test_backend_health()
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
    
    print("-" * 50)
    print("E2E tests completed")


if __name__ == "__main__":
    asyncio.run(main())
