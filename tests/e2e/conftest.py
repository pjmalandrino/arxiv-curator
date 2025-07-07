"""
E2E test configuration using pytest-playwright
"""
import pytest


# Use pytest-playwright fixtures directly
# The plugin provides:
# - browser
# - browser_context_args
# - browser_type_launch_args
# - page
# etc.

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }
