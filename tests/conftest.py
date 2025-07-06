"""Test configuration and fixtures."""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import Config, DatabaseConfig, ArxivConfig, HuggingFaceConfig
from src.infrastructure import DatabaseSession


@pytest.fixture
def test_config():
    """Create test configuration."""
    return Config(
        database=DatabaseConfig(
            url="postgresql://curator:testpassword@localhost:5433/arxiv_curator_test"
        ),
        arxiv=ArxivConfig(
            categories=["cs.CL", "cs.AI"],
            keywords=["test", "paper"],
            max_results=5
        ),
        huggingface=HuggingFaceConfig(
            api_key="test_token",
            model="test/model"
        ),
        ollama=None,
        processing=None
    )


@pytest.fixture
def db_session(test_config):
    """Create test database session."""
    session = DatabaseSession(test_config.database)
    session.create_tables()
    yield session
    # Cleanup would go here
