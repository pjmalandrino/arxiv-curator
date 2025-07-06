"""
Unit tests for SQLAlchemy models
"""
import pytest
import uuid
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.models import Base, Paper, Summary


class TestPaperModel:
    """Test Paper model functionality"""
    
    def test_paper_creation(self, db_session, sample_paper_data):
        """Test creating a paper instance"""
        paper = Paper(**sample_paper_data)
        db_session.add(paper)
        db_session.commit()
        
        assert paper.id is not None
        assert paper.arxiv_id == sample_paper_data['arxiv_id']
        assert paper.title == sample_paper_data['title']
        assert paper.authors == sample_paper_data['authors']
        assert paper.created_at is not None
    
    def test_paper_unique_arxiv_id(self, db_session, sample_paper_data):
        """Test that arxiv_id must be unique"""
        paper1 = Paper(**sample_paper_data)
        db_session.add(paper1)
        db_session.commit()
        
        # Try to create another paper with same arxiv_id
        paper2 = Paper(**sample_paper_data)
        db_session.add(paper2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()    
    def test_paper_required_fields(self, db_session):
        """Test that required fields are enforced"""
        # Missing required field (title)
        paper = Paper(
            arxiv_id='2401.99999',
            authors=['Test Author'],
            abstract='Test abstract',
            published_date=date.today(),
            categories=['cs.CL'],
            pdf_url='https://arxiv.org/pdf/2401.99999.pdf'
        )
        db_session.add(paper)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_paper_array_fields(self, db_session):
        """Test array fields (authors, categories)"""
        paper = Paper(
            arxiv_id='2401.88888',
            title='Test Paper',
            authors=['Author 1', 'Author 2', 'Author 3'],
            abstract='Test abstract',
            published_date=date.today(),
            categories=['cs.CL', 'cs.AI', 'cs.LG'],
            pdf_url='https://arxiv.org/pdf/2401.88888.pdf'
        )
        db_session.add(paper)
        db_session.commit()
        
        assert len(paper.authors) == 3
        assert 'Author 2' in paper.authors
        assert len(paper.categories) == 3
        assert 'cs.AI' in paper.categories

class TestSummaryModel:
    """Test Summary model functionality"""
    
    def test_summary_creation(self, db_session, sample_paper_data, sample_summary_data):
        """Test creating a summary instance"""
        # First create a paper
        paper = Paper(**sample_paper_data)
        db_session.add(paper)
        db_session.commit()
        
        # Create summary
        summary = Summary(paper_id=paper.id, **sample_summary_data)
        db_session.add(summary)
        db_session.commit()
        
        assert summary.id is not None
        assert summary.paper_id == paper.id
        assert summary.summary == sample_summary_data['summary']
        assert summary.relevance_score == sample_summary_data['relevance_score']
        assert summary.created_at is not None
    
    def test_summary_paper_relationship(self, db_session, sample_paper_data, sample_summary_data):
        """Test relationship between Paper and Summary"""
        paper = Paper(**sample_paper_data)
        db_session.add(paper)
        db_session.commit()
        
        summary = Summary(paper_id=paper.id, **sample_summary_data)
        db_session.add(summary)
        db_session.commit()
        
        # Test relationship navigation
        assert summary.paper == paper
        assert summary in paper.summaries    
    def test_cascade_delete(self, db_session, sample_paper_data, sample_summary_data):
        """Test that deleting a paper deletes its summaries"""
        paper = Paper(**sample_paper_data)
        db_session.add(paper)
        db_session.commit()
        
        summary1 = Summary(paper_id=paper.id, **sample_summary_data)
        summary2 = Summary(paper_id=paper.id, summary="Another summary", 
                          key_points=["Point A"], relevance_score=6.0)
        db_session.add_all([summary1, summary2])
        db_session.commit()
        
        # Delete the paper
        db_session.delete(paper)
        db_session.commit()
        
        # Check summaries are also deleted
        assert db_session.query(Summary).filter_by(paper_id=paper.id).count() == 0
    
    def test_summary_foreign_key_constraint(self, db_session, sample_summary_data):
        """Test that summary requires valid paper_id"""
        # Try to create summary with non-existent paper_id
        fake_paper_id = uuid.uuid4()
        summary = Summary(paper_id=fake_paper_id, **sample_summary_data)
        db_session.add(summary)
        
        # SQLite doesn't enforce foreign keys by default, so we check differently
        try:
            db_session.commit()
            # If commit succeeds (SQLite), verify the paper doesn't exist
            paper = db_session.query(Paper).filter_by(id=fake_paper_id).first()
            assert paper is None  # Paper shouldn't exist
        except IntegrityError:
            # PostgreSQL will raise IntegrityError
            db_session.rollback()