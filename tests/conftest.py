"""
Global pytest configuration and fixtures for arXiv curator tests
"""
import os
import sys
import pytest
import tempfile
from datetime import datetime, date
from unittest.mock import Mock, MagicMock
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import Base, Paper, Summary
from src.database import DatabaseManager
from src.arxiv_client import ArxivClient
from src.hf_client import HuggingFaceClient


# Test database configuration
@pytest.fixture(scope="function")
def test_db():
    """Create a temporary SQLite database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_url = f"sqlite:///{tmp.name}"
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        
        yield db_url
        
        # Cleanup
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def db_session(test_db):
    """Create a database session for testing"""
    engine = create_engine(test_db)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def db_manager(test_db):
    """Create a DatabaseManager instance with test database"""
    return DatabaseManager(test_db)


@pytest.fixture
def sample_paper_data():
    """Sample paper data for testing"""
    return {
        'arxiv_id': '2401.12345',
        'title': 'Advances in Large Language Models: A Comprehensive Survey',
        'authors': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'abstract': 'This paper presents a comprehensive survey of recent advances in large language models (LLMs). '
                   'We review the latest architectures, training methodologies, and applications. '
                   'Our analysis covers transformer-based models, including GPT, BERT, and their variants. '
                   'We discuss key challenges such as computational efficiency, bias mitigation, and interpretability.',
        'published_date': date(2024, 1, 15),
        'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
        'pdf_url': 'https://arxiv.org/pdf/2401.12345.pdf'
    }


@pytest.fixture
def sample_summary_data():
    """Sample summary data for testing"""
    return {
        'summary': 'This survey examines recent LLM developments, covering architectures, training, and applications.',
        'key_points': [
            'Comprehensive review of transformer architectures',
            'Analysis of training methodologies',
            'Discussion of practical applications',
            'Challenges in efficiency and bias'
        ],
        'relevance_score': 8.5,
        'model_used': 'facebook/bart-large-cnn'
    }


@pytest.fixture
def mock_arxiv_client(mocker):
    """Mock ArxivClient for testing"""
    client = mocker.Mock(spec=ArxivClient)
    client.categories = ['cs.CL', 'cs.AI']
    client.keywords = ['LLM', 'language model']
    return client


@pytest.fixture
def mock_hf_client(mocker):
    """Mock HuggingFaceClient for testing"""
    client = mocker.Mock(spec=HuggingFaceClient)
    client.model = 'facebook/bart-large-cnn'
    client.summarize_paper = mocker.Mock(return_value={
        'summary': 'Test summary',
        'key_points': ['Point 1', 'Point 2'],
        'relevance_score': 7.5
    })
    return client


@pytest.fixture
def mock_arxiv_papers():
    """Mock arXiv API response papers"""
    return [
        {
            'arxiv_id': '2401.12345',
            'title': 'Advances in Large Language Models',
            'authors': ['John Doe', 'Jane Smith'],
            'abstract': 'This paper presents advances in LLMs...',
            'published_date': datetime(2024, 1, 15),
            'categories': ['cs.CL', 'cs.AI'],
            'pdf_url': 'https://arxiv.org/pdf/2401.12345.pdf'
        },
        {
            'arxiv_id': '2401.12346',
            'title': 'Transformer Architecture Improvements',
            'authors': ['Alice Brown', 'Bob Wilson'],
            'abstract': 'We propose novel improvements to transformer architecture...',
            'published_date': datetime(2024, 1, 16),
            'categories': ['cs.CL', 'cs.LG'],
            'pdf_url': 'https://arxiv.org/pdf/2401.12346.pdf'
        }
    ]


# Environment variables for testing
@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')
    monkeypatch.setenv('HF_TOKEN', 'test-token')
    monkeypatch.setenv('HF_MODEL', 'facebook/bart-large-cnn')
    monkeypatch.setenv('PYTHONPATH', os.path.dirname(os.path.dirname(__file__)))
