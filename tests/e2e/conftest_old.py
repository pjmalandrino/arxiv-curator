"""
E2E Test Configuration and Fixtures
"""
import os
import pytest
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Generator, Dict, Any
import requests
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from tests.e2e.utils.keycloak_admin import KeycloakTestAdmin
from tests.e2e.utils.database_utils import DatabaseHelper
from tests.e2e.config.test_config import TestConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """Launch browser for tests"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=TestConfig.HEADLESS,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        yield browser
        await browser.close()


@pytest.fixture(scope="function")
async def context(browser: Browser):
    """Create browser context with viewport and permissions"""
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        ignore_https_errors=True,
        locale='en-US'
    )
    yield context
    await context.close()


@pytest.fixture(scope="function")
async def page(context: BrowserContext):
    """Create new page for each test"""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture(scope="session")
def keycloak_admin():
    """Initialize Keycloak admin client"""
    admin = KeycloakTestAdmin(
        server_url=TestConfig.KEYCLOAK_URL,
        admin_username=TestConfig.KEYCLOAK_ADMIN_USER,
        admin_password=TestConfig.KEYCLOAK_ADMIN_PASSWORD,
        realm_name=TestConfig.KEYCLOAK_REALM
    )
    # Wait for Keycloak to be ready
    admin.wait_for_keycloak()
    yield admin


@pytest.fixture(scope="session")
def database():
    """Initialize database helper"""
    db = DatabaseHelper(TestConfig.DATABASE_URL)
    yield db
    db.close()


@pytest.fixture(scope="function")
def test_users(keycloak_admin):
    """Create test users with different roles"""
    users = {
        'admin': {
            'username': 'test_admin',
            'password': 'Test123!',
            'email': 'admin@test.com',
            'roles': ['admin', 'user']
        },
        'user': {
            'username': 'test_user',
            'password': 'Test123!',
            'email': 'user@test.com',
            'roles': ['user']
        },
        'viewer': {
            'username': 'test_viewer',
            'password': 'Test123!',
            'email': 'viewer@test.com',
            'roles': []
        }
    }
    
    created_users = {}
    for role, user_data in users.items():
        user_id = keycloak_admin.create_test_user(**user_data)
        created_users[role] = {**user_data, 'id': user_id}
    
    yield created_users
    
    # Cleanup
    for user in created_users.values():
        keycloak_admin.delete_user(user['id'])


@pytest.fixture(scope="function")
def api_client():
    """Create API client for backend testing"""
    from .fixtures.api import APIClient
    return APIClient(TestConfig.API_BASE_URL)


@pytest.fixture(scope="function")
async def authenticated_page(page: Page, test_users):
    """Provide authenticated page with user login"""
    from .pages.login_page import LoginPage
    
    login_page = LoginPage(page)
    await login_page.navigate()
    await login_page.login(
        test_users['user']['username'],
        test_users['user']['password']
    )
    yield page


@pytest.fixture(scope="function")
async def admin_page(page: Page, test_users):
    """Provide authenticated page with admin login"""
    from .pages.login_page import LoginPage
    
    login_page = LoginPage(page)
    await login_page.navigate()
    await login_page.login(
        test_users['admin']['username'],
        test_users['admin']['password']
    )
    yield page


@pytest.fixture(scope="function")
def sample_papers(database):
    """Create sample papers for testing"""
    papers = [
        {
            'arxiv_id': 'test.1234',
            'title': 'Test Paper 1',
            'authors': ['Author A', 'Author B'],
            'abstract': 'This is a test abstract for paper 1',
            'categories': ['cs.AI'],
            'summary': 'AI generated summary 1'
        },
        {
            'arxiv_id': 'test.5678',
            'title': 'Test Paper 2',
            'authors': ['Author C'],
            'abstract': 'This is a test abstract for paper 2',
            'categories': ['cs.ML'],
            'summary': 'AI generated summary 2'
        }
    ]
    
    created_ids = database.create_papers(papers)
    yield papers
    database.delete_papers(created_ids)
