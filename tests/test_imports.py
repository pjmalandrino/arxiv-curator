"""Test imports and basic functionality."""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_core_imports():
    """Test that core modules can be imported."""
    from src.core.config import Config, DatabaseConfig, ArxivConfig, HuggingFaceConfig
    from src.core.exceptions import ArxivCuratorError, DatabaseError
    
    assert Config is not None
    assert DatabaseConfig is not None
    assert ArxivCuratorError is not None


def test_domain_imports():
    """Test that domain modules can be imported."""
    from src.domain.entities import Paper, Summary, PaperMetadata, SummaryResult
    from src.domain.value_objects import ArxivId, Score, Category
    
    assert Paper is not None
    assert ArxivId is not None


def test_infrastructure_imports():
    """Test that infrastructure modules can be imported."""
    # These imports might fail without database dependencies
    try:
        from src.infrastructure.database import DatabaseSession, DatabaseManager
        from src.infrastructure.arxiv import ArxivClient
        from src.infrastructure.huggingface import HuggingFaceClient
        assert DatabaseSession is not None
        assert ArxivClient is not None
    except ImportError as e:
        pytest.skip(f"Infrastructure imports require dependencies: {e}")


def test_service_imports():
    """Test that service modules can be imported."""
    try:
        from src.services.curation_service import CurationService
        from src.services.pipeline_service import PipelineService
        assert CurationService is not None
        assert PipelineService is not None
    except ImportError as e:
        pytest.skip(f"Service imports require dependencies: {e}")


def test_web_imports():
    """Test that web modules can be imported."""
    try:
        from src.web.app import create_app
        from src.web.routes import papers_bp, api_bp
        assert create_app is not None
        assert papers_bp is not None
    except ImportError as e:
        pytest.skip(f"Web imports require dependencies: {e}")
