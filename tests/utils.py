"""
Test utilities and helper functions
"""
import os
import json
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Paper, Summary


def setup_test_database(db_url=None):
    """Set up a test database"""
    if not db_url:
        db_url = "sqlite:///test.db"
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    return engine


def teardown_test_database(engine):
    """Clean up test database"""
    Base.metadata.drop_all(engine)
    engine.dispose()


def create_test_paper(**kwargs):
    """Create a test paper with default values"""
    defaults = {
        'arxiv_id': f'2401.{datetime.now().microsecond:05d}',
        'title': 'Test Paper',
        'authors': ['Test Author'],
        'abstract': 'Test abstract',
        'published_date': date.today(),
        'categories': ['cs.CL'],
        'pdf_url': 'https://arxiv.org/pdf/test.pdf'
    }
    defaults.update(kwargs)
    return Paper(**defaults)


def create_test_summary(paper_id, **kwargs):
    """Create a test summary with default values"""
    defaults = {
        'paper_id': paper_id,
        'summary': 'Test summary',
        'key_points': ['Point 1', 'Point 2'],
        'relevance_score': 7.5,
        'model_used': 'test-model'
    }
    defaults.update(kwargs)
    return Summary(**defaults)

def assert_paper_equal(paper1, paper2):
    """Assert two papers have the same content"""
    assert paper1.arxiv_id == paper2.arxiv_id
    assert paper1.title == paper2.title
    assert paper1.authors == paper2.authors
    assert paper1.abstract == paper2.abstract
    assert paper1.published_date == paper2.published_date
    assert set(paper1.categories) == set(paper2.categories)
    assert paper1.pdf_url == paper2.pdf_url


def assert_summary_equal(summary1, summary2):
    """Assert two summaries have the same content"""
    assert summary1.paper_id == summary2.paper_id
    assert summary1.summary == summary2.summary
    assert set(summary1.key_points) == set(summary2.key_points)
    assert abs(summary1.relevance_score - summary2.relevance_score) < 0.01
    assert summary1.model_used == summary2.model_used


def load_test_fixture(filename):
    """Load test data from JSON fixture"""
    fixture_path = os.path.join(
        os.path.dirname(__file__), 
        'fixtures', 
        filename
    )
    with open(fixture_path, 'r') as f:
        return json.load(f)


def mock_arxiv_response(papers):
    """Create mock arXiv API response"""
    class MockResult:
        def __init__(self, paper_data):
            self.entry_id = f"http://arxiv.org/abs/{paper_data['arxiv_id']}v1"
            self.title = paper_data['title']
            self.authors = [type('Author', (), {'name': name}) 
                          for name in paper_data['authors']]
            self.summary = paper_data['abstract']
            self.published = paper_data['published_date']
            self.categories = paper_data['categories']
            self.pdf_url = paper_data['pdf_url']
    
    return [MockResult(p) for p in papers]